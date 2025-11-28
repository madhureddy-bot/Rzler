from typing import List, Dict
import inspect
import logging

# Monkey patch for chumpy/smplx compatibility with Python 3.11+
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

import numpy as np

# Monkey patch for chumpy compatibility with newer numpy versions
try:
    np.bool = bool
    np.int = int
    np.float = float
    np.complex = complex
    np.object = object
    np.str = str
    np.unicode = str
except AttributeError:
    pass

import trimesh
import torch
import smplx
import os

from .measurement_definitions import *
from .utils import *
from .landmark_definitions import *
from .joint_definitions import *

logger = logging.getLogger(__name__)


def set_shape(model, shape_coefs):
    '''
    Set shape of body model.
    :param model: smplx body model
    :param shape_coefs: torch.tensor dim (10,)

    Return
    shaped smplx body model
    '''
    shape_coefs = shape_coefs.to(torch.float32)
    return model(betas=shape_coefs, return_verts=True)

def create_model(model_type, model_root, gender, num_betas=10, num_thetas=24):
    '''
    Create SMPL/SMPLX/etc. body model
    :param model_type: str of model type: smpl, smplx, etc.
    :param model_root: str of location where there are smpl/smplx/etc. folders with .pkl models
                        (clumsy definition in smplx package)
    :param gender: str of gender: MALE or FEMALE or NEUTRAL
    :param num_betas: int of number of shape coefficients
                      requires the model with num_coefs in model_root
    :param num_thetas: int of number of pose coefficients
    
    Return:
    :param smplx body model (SMPL, SMPLX, etc.)
    '''
    
    return smplx.create(model_path=model_root,
                        model_type=model_type,
                        gender=gender, 
                        use_face_contour=False,
                        num_betas=num_betas,
                        ext='pkl')


class Measurer():
    '''
    Measure a parametric body model defined either.
    Parent class for Measure{SMPL,SMPLX,..}.

    All the measurements are expressed in cm.
    '''

    def __init__(self):
        self.verts = None
        self.faces = None
        self.joints = None
        self.gender = None

        self.measurements = {}
        self.height_normalized_measurements = {}
        self.labeled_measurements = {}
        self.height_normalized_labeled_measurements = {}
        self.labels2names = {}

    def from_verts(self):
        pass

    def from_body_model(self):
        pass

    def measure(self, 
                measurement_names: List[str]
                ):
        '''
        Measure the given measurement names from measurement_names list
        :param measurement_names - list of strings of defined measurements
                                    to measure from MeasurementDefinitions class
        '''

        for m_name in measurement_names:
            if m_name not in self.all_possible_measurements:
                logger.warning(f"Measurement {m_name} not defined.")
                continue

            if m_name in self.measurements:
                continue

            try:
                if self.measurement_types[m_name] == MeasurementType().LENGTH:
                    value = self.measure_length(m_name)
                    self.measurements[m_name] = value

                elif self.measurement_types[m_name] == MeasurementType().CIRCUMFERENCE:
                    value = self.measure_circumference(m_name)
                    self.measurements[m_name] = value
        
                else:
                    logger.warning(f"Measurement {m_name} not defined")
            except Exception as e:
                logger.warning(f"Failed to measure {m_name}: {e}")

    def measure_length(self, measurement_name: str):
        '''
        Measure distance between 2+ landmarks.
        For 2 landmarks: straight-line distance
        For 3+ landmarks: path distance (sum of consecutive segments)
        :param measurement_name: str - defined in MeasurementDefinitions

        Returns
        :float of measurement in cm
        '''

        measurement_landmarks_inds = self.length_definitions[measurement_name]
        num_landmarks = len(measurement_landmarks_inds)

        landmark_points = []
        for i in range(num_landmarks):
            if isinstance(measurement_landmarks_inds[i], tuple):
                # if tuple of indices for landmark, take their average
                lm = (self.verts[measurement_landmarks_inds[i][0]] + 
                          self.verts[measurement_landmarks_inds[i][1]]) / 2
            else:
                lm = self.verts[measurement_landmarks_inds[i]]
            
            landmark_points.append(lm)

        if num_landmarks == 2:
            # Standard 2-point distance
            landmark_points = np.vstack(landmark_points)[None, ...]
            return self._get_dist(landmark_points)
        elif num_landmarks >= 3:
            # Multi-point path distance: sum of consecutive segments
            total_distance = 0
            for i in range(num_landmarks - 1):
                segment = np.array([[landmark_points[i], landmark_points[i + 1]]])
                total_distance += self._get_dist(segment)
            return total_distance
        else:
            raise ValueError(f"Measurement {measurement_name} has {num_landmarks} landmarks. At least 2 are required.")

    @staticmethod
    def _get_dist(verts: np.ndarray) -> float:
        '''
        The Euclidean distance between vertices.
        The distance is found as the sum of each pair i 
        of 3D vertices (i,0,:) and (i,1,:) 
        :param verts: np.ndarray (N,2,3) - vertices used 
                        to find distances
        
        Returns:
        :param dist: float, sumed distances between vertices
        '''

        verts_distances = np.linalg.norm(verts[:, 1] - verts[:, 0],axis=1)
        distance = np.sum(verts_distances)
        distance_cm = distance * 100 # convert to cm
        return distance_cm
    
    def measure_circumference(self, 
                              measurement_name: str, 
                              ):
        '''
        Measure circumferences. Circumferences are defined with 
        landmarks and joints - the measurement is found by cutting the 
        SMPL model with the  plane defined by a point (landmark point) and 
        normal (vector connecting the two joints).
        :param measurement_name: str - measurement name

        Return
        float of measurement value in cm
        '''

        measurement_definition = self.circumf_definitions[measurement_name]
        circumf_landmarks = measurement_definition["LANDMARKS"]
        circumf_landmark_indices = [self.landmarks[l_name] for l_name in circumf_landmarks]
        circumf_n1, circumf_n2 = self.circumf_definitions[measurement_name]["JOINTS"]
        circumf_n1, circumf_n2 = self.joint2ind[circumf_n1], self.joint2ind[circumf_n2]
        
        plane_origin = np.mean(self.verts[circumf_landmark_indices,:],axis=0)
        plane_normal = self.joints[circumf_n1,:] - self.joints[circumf_n2,:]

        mesh = trimesh.Trimesh(vertices=self.verts, faces=self.faces)

        # new version            
        slice_segments, sliced_faces = trimesh.intersections.mesh_plane(mesh, 
                                plane_normal=plane_normal, 
                                plane_origin=plane_origin, 
                                return_faces=True) # (N, 2, 3), (N,)
        
        slice_segments = filter_body_part_slices(slice_segments,
                                                 sliced_faces,
                                                 measurement_name,
                                                 self.circumf_2_bodypart,
                                                 self.face_segmentation)
        
        slice_segments_hull = convex_hull_from_3D_points(slice_segments)

        return self._get_dist(slice_segments_hull)

    def height_normalize_measurements(self, new_height: float):
        ''' 
        Scale all measurements so that the height measurement gets
        the value of new_height:
        new_measurement = (old_measurement / old_height) * new_height
        NOTE the measurements and body model remain unchanged, a new
        dictionary height_normalized_measurements is created.
        
        Input:
        :param new_height: float, the newly defined height.

        Return:
        self.height_normalized_measurements: dict of 
                {measurement:value} pairs with 
                height measurement = new_height, and other measurements
                scaled accordingly
        '''
        # Input validation
        if not isinstance(new_height, (int, float)):
            raise TypeError(f"new_height must be a number, got {type(new_height)}")
        
        if not 30 <= new_height <= 300:
            raise ValueError(f"Height {new_height} cm is unrealistic (should be 30-300 cm)")
        
        if not self.measurements:
            raise ValueError("No measurements available. Call measure() first.")
        
        if "height" not in self.measurements:
            raise ValueError("Must measure 'height' before normalizing. Add 'height' to measurement_names.")
        
        if self.measurements != {}:
            old_height = self.measurements["height"]
            for m_name, m_value in self.measurements.items():
                norm_value = (m_value / old_height) * new_height
                self.height_normalized_measurements[m_name] = norm_value

            if self.labeled_measurements != {}:
                for m_name, m_value in self.labeled_measurements.items():
                    norm_value = (m_value / old_height) * new_height
                    self.height_normalized_labeled_measurements[m_name] = norm_value

    def label_measurements(self,set_measurement_labels: Dict[str, str]):
        '''
        Create labeled_measurements dictionary with "label: x cm" structure
        for each given measurement.
        NOTE: This overwrites any prior labeling!
        
        :param set_measurement_labels: dict of labels and measurement names
                                        (example. {"A": "head_circumference"})
        '''

        if self.labeled_measurements != {}:
            logger.info("Overwriting old labels")

        self.labeled_measurements = {}
        self.labels2names = {}

        for set_label, set_name in set_measurement_labels.items():
            
            if set_name not in self.all_possible_measurements:
                logger.warning(f"Measurement {set_name} not defined.")
                pass

            if set_name not in self.measurements.keys():
                self.measure([set_name])

            self.labeled_measurements[set_label] = self.measurements[set_name]
            self.labels2names[set_label] = set_name


def get_joint_regressor(model_type, model_root, gender, num_thetas):
    '''Get joint regressor matrix for computing joints from vertices'''
    model = create_model(model_type=model_type,
                        model_root=model_root,
                        gender=gender,
                        num_betas=10,
                        num_thetas=num_thetas)
    return model.J_regressor


class MeasureSMPL(Measurer):
    '''
    Measure the SMPL model defined either by the shape parameters or
    by its 6890 vertices. 

    All the measurements are expressed in cm.
    '''

    def __init__(self, body_model_root=None):
        
        super().__init__()

        self.model_type = "smpl"

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))

        # Use provided root or default to ROMP's smpl_model_data
        if body_model_root is None:
            body_model_root = os.path.join(self.project_root, "data", "smpl_models")

        self.body_model_root = body_model_root
        # SMPL files are in the smpl subdirectory
        self.body_model_path = os.path.join(self.body_model_root, "smpl")

        self.faces = smplx.SMPL(self.body_model_path, ext="pkl").faces
        
        # Path to body segmentation file
        face_segmentation_path = os.path.join(
            self.project_root,
            "data",
            "body_measurements",
            "smpl",
            "smpl_body_parts_2_faces.json"
        )
        self.face_segmentation = load_face_segmentation(face_segmentation_path)

        self.landmarks = SMPL_LANDMARK_INDICES
        self.measurement_types = MEASUREMENT_TYPES
        self.length_definitions = SMPLMeasurementDefinitions().LENGTHS
        self.circumf_definitions = SMPLMeasurementDefinitions().CIRCUMFERENCES
        self.circumf_2_bodypart = SMPLMeasurementDefinitions().CIRCUMFERENCE_TO_BODYPARTS
        self.all_possible_measurements = SMPLMeasurementDefinitions().possible_measurements

        self.joint2ind = SMPL_JOINT2IND
        self.num_joints = SMPL_NUM_JOINTS

        self.num_points = 6890

    def from_verts(self,
                   verts: torch.tensor):
        '''
        Construct body model from only vertices.
        :param verts: torch.tensor (6890,3) of SMPL vertices
        '''        

        verts = verts.squeeze()
        error_msg = f"verts need to be of dimension ({self.num_points},3)"
        assert verts.shape == torch.Size([self.num_points,3]), error_msg

        joint_regressor = get_joint_regressor(self.model_type, 
                                              self.body_model_root,
                                              gender="NEUTRAL", 
                                              num_thetas=self.num_joints)
        joints = torch.matmul(joint_regressor, verts)
        self.joints = joints.numpy()
        self.verts = verts.numpy()

    def from_body_model(self,
                        gender: str,
                        shape: torch.tensor):
        '''
        Construct body model from given gender and shape params 
        of SMPL model.
        :param gender: str, MALE or FEMALE or NEUTRAL
        :param shape: torch.tensor, (1,10) beta parameters
                                    for SMPL model
        '''  

        model = create_model(model_type=self.model_type, 
                             model_root=self.body_model_root, 
                             gender=gender,
                             num_betas=10,
                             num_thetas=self.num_joints)    
        model_output = set_shape(model, shape)
        
        self.verts = model_output.vertices.detach().cpu().numpy().squeeze()
        self.joints = model_output.joints.squeeze().detach().cpu().numpy()
        self.gender = gender

class MeasureBody():
    def __new__(cls, model_type, body_model_root=None):
        model_type = model_type.lower()
        if model_type == 'smpl':
            return MeasureSMPL(body_model_root=body_model_root)
        else:
            raise NotImplementedError("Model type not defined. Only 'smpl' is supported for ROMP.")
