
from .landmark_definitions import *
from .joint_definitions import *

STANDARD_LABELS = {
        'B': 'neck',
        'C': 'front_suit_coat_blazer_length',
        'D': 'full_chest_horizontal',
        'E': 'full_stomach_horizontal',
        'F': 'hips_seat_width',
        'G': 'wrist_width_cuff',
        'H': 'biceps',
        'I': 'forearms',
        'J': 'full_sleeve',
        'K': 'inside leg height',
        'L': 'thigh_width',
        'M': 'calf_width',
        'N': 'leg_opening_leg_bottom',
        'O': 'full_shoulder_width',
        'P': 'height',
        'Q': 'out_seam_length'
    }


class MeasurementType():
    CIRCUMFERENCE = "circumference"
    LENGTH = "length"


MEASUREMENT_TYPES = {
        "height": MeasurementType.LENGTH,
        "neck": MeasurementType.CIRCUMFERENCE,
        "front_suit_coat_blazer_length": MeasurementType.LENGTH,
        "full_chest_horizontal": MeasurementType.CIRCUMFERENCE,
        "full_stomach_horizontal": MeasurementType.CIRCUMFERENCE,
        "waist_width": MeasurementType.CIRCUMFERENCE,
        "hips_seat_width": MeasurementType.CIRCUMFERENCE,
        "wrist_width_cuff": MeasurementType.CIRCUMFERENCE,
        "biceps": MeasurementType.CIRCUMFERENCE,
        "forearms": MeasurementType.CIRCUMFERENCE,
        "full_sleeve": MeasurementType.LENGTH,
        "inside leg height": MeasurementType.LENGTH,
        "thigh_width": MeasurementType.CIRCUMFERENCE,
        "calf_width": MeasurementType.CIRCUMFERENCE,
        "leg_opening_leg_bottom": MeasurementType.CIRCUMFERENCE,
        "knee_width": MeasurementType.CIRCUMFERENCE,
        "full_shoulder_width": MeasurementType.LENGTH,
        "full_crotch_vertical": MeasurementType.LENGTH,
        "out_seam_length": MeasurementType.LENGTH
    }

class SMPLMeasurementDefinitions():
    '''
    Definition of SMPL measurements.

    To add a new measurement:
    1. add it to the measurement_types dict and set the type:
       LENGTH or CIRCUMFERENCE
    2. depending on the type, define the measurement in LENGTHS or 
       CIRCUMFERENCES dict
       - LENGTHS are defined using 2 landmarks - the measurement is 
                found with distance between landmarks
       - CIRCUMFERENCES are defined with landmarks and joints - the 
                measurement is found by cutting the SMPL model with the 
                plane defined by a point (landmark point) and normal (
                vector connecting the two joints)
    3. If the body part is a CIRCUMFERENCE, a possible issue that arises is
       that the plane cutting results in multiple body part slices. To alleviate
       that, define the body part where the measurement should be located in 
       CIRCUMFERENCE_TO_BODYPARTS dict. This way, only slice in that body part is
       used for finding the measurement. The body parts are defined by the SMPL 
       face segmentation.
    '''
    
    LENGTHS = {"height": 
                    (SMPL_LANDMARK_INDICES["HEAD_TOP"], 
                     SMPL_LANDMARK_INDICES["HEELS"]
                     ),
               "front_suit_coat_blazer_length":
                    (SMPL_LANDMARK_INDICES["SHOULDER_TOP"], 
                     SMPL_LANDMARK_INDICES["INSEAM_POINT"]
                    ),
                "full_sleeve":
                    (SMPL_LANDMARK_INDICES["RIGHT_SHOULDER"], 
                     SMPL_LANDMARK_INDICES["RIGHT_WRIST"]
                    ),
                "inside leg height": 
                    (SMPL_LANDMARK_INDICES["LOW_LEFT_HIP"], 
                     SMPL_LANDMARK_INDICES["LEFT_ANKLE"]
                    ),
                "full_shoulder_width":
                    (SMPL_LANDMARK_INDICES["LEFT_SHOULDER"], 
                     SMPL_LANDMARK_INDICES["RIGHT_SHOULDER"]
                    ),
                 "full_crotch_vertical":
                    (SMPL_LANDMARK_INDICES["FRONT_WAISTBAND"],   # Belly button front
                     SMPL_LANDMARK_INDICES["PUBIC_BONE"],        # Lower front
                     SMPL_LANDMARK_INDICES["CROTCH"],            # Crotch bottom
                     SMPL_LANDMARK_INDICES["BACK_WAISTBAND"]     # Belly button back
                    ),
                "out_seam_length":
                    (SMPL_LANDMARK_INDICES["LEFT_WAIST_SIDE"],
                     SMPL_LANDMARK_INDICES["LEFT_HEEL"]
                    ),
               }

    # defined with landmarks and joints
    # landmarks are defined with indices of the smpl model points
    # normals are defined with joint names of the smpl model
    CIRCUMFERENCES = {
        "neck":{"LANDMARKS":["NECK_ADAM_APPLE"],
                "JOINTS":["spine2","head"]},
        "full_chest_horizontal":{"LANDMARKS":["LEFT_NIPPLE","RIGHT_NIPPLE"],
                                 "JOINTS":["pelvis","spine3"]},
        "full_stomach_horizontal":{"LANDMARKS":["BELLY_BUTTON","BACK_BELLY_BUTTON"],
                                   "JOINTS":["pelvis","spine3"]},
        "waist_width":{"LANDMARKS":["FRONT_STOMACH","BACK_STOMACH"],
                       "JOINTS":["pelvis","spine3"]},
        "hips_seat_width":{"LANDMARKS":["PUBIC_BONE"],
                           "JOINTS":["pelvis","spine3"]},
        "wrist_width_cuff":{"LANDMARKS":["RIGHT_WRIST"],
                            "JOINTS":["right_wrist","right_hand"]},
        "biceps":{"LANDMARKS":["RIGHT_BICEP"],
                  "JOINTS":["right_shoulder","right_elbow"]},
        "forearms":{"LANDMARKS":["RIGHT_FOREARM"],
                    "JOINTS":["right_elbow","right_wrist"]},
        "thigh_width":{"LANDMARKS":["LEFT_THIGH"],
                       "JOINTS":["pelvis","spine3"]},
        "calf_width":{"LANDMARKS":["LEFT_CALF"],
                      "JOINTS":["pelvis","spine3"]},
        "leg_opening_leg_bottom":{"LANDMARKS":["LEFT_ANKLE","LEFT_HEEL"],
                                   "JOINTS":["left_ankle","left_foot"]},
        "knee_width":{"LANDMARKS":["RIGHT_KNEE"],
                      "JOINTS":["pelvis","spine3"]},
                     
                     }
    
    possible_measurements = list(LENGTHS.keys()) + list(CIRCUMFERENCES.keys())

    CIRCUMFERENCE_TO_BODYPARTS = {
        "neck":"neck",
        "full_chest_horizontal":["spine1","spine2"],
        "full_stomach_horizontal":["hips","spine"],
        "waist_width":["hips","spine"],
        "hips_seat_width":"hips",
        "wrist_width_cuff":["rightHand","rightForeArm"],
        "biceps":"rightArm",
        "forearms":"rightForeArm",
        "thigh_width": "leftUpLeg",
        "calf_width": "leftLeg",
        "leg_opening_leg_bottom": ["leftLeg", "leftFoot"],
        "knee_width": ["rightUpLeg", "rightLeg"],
    }



class SMPLXMeasurementDefinitions():
    '''
    Definition of SMPLX measurements.

    To add a new measurement:
    1. add it to the measurement_types dict and set the type:
       LENGTH or CIRCUMFERENCE
    2. depending on the type, define the measurement in LENGTHS or 
       CIRCUMFERENCES dict
       - LENGTHS are defined using 2 landmarks - the measurement is 
                found with distance between landmarks
       - CIRCUMFERENCES are defined with landmarks and joints - the 
                measurement is found by cutting the SMPLX model with the 
                plane defined by a point (landmark point) and normal (
                vector connecting the two joints)
    3. If the body part is a CIRCUMFERENCE, a possible issue that arises is
       that the plane cutting results in multiple body part slices. To alleviate
       that, define the body part where the measurement should be located in 
       CIRCUMFERENCE_TO_BODYPARTS dict. This way, only slice in that body part is
       used for finding the measurement. The body parts are defined by the SMPL 
       face segmentation.
    '''
    
    LENGTHS = {"height": 
                    (SMPLX_LANDMARK_INDICES["HEAD_TOP"], 
                     SMPLX_LANDMARK_INDICES["HEELS"]
                     ),
               "front_suit_coat_blazer_length":
                    (SMPLX_LANDMARK_INDICES["SHOULDER_TOP"], 
                     SMPLX_LANDMARK_INDICES["INSEAM_POINT"]
                    ),
                "full_sleeve":
                    (SMPLX_LANDMARK_INDICES["RIGHT_SHOULDER"], 
                     SMPLX_LANDMARK_INDICES["RIGHT_WRIST"]
                    ),
                "inside leg height": 
                    (SMPLX_LANDMARK_INDICES["LOW_LEFT_HIP"], 
                     SMPLX_LANDMARK_INDICES["LEFT_ANKLE"]
                    ),
                "full_shoulder_width":
                    (SMPLX_LANDMARK_INDICES["LEFT_SHOULDER"], 
                     SMPLX_LANDMARK_INDICES["RIGHT_SHOULDER"]
                    ),
                "full_crotch_vertical":
                    (SMPLX_LANDMARK_INDICES["FRONT_WAISTBAND"],  # Belly button front
                     SMPLX_LANDMARK_INDICES["PUBIC_BONE"],       # Lower front
                     SMPLX_LANDMARK_INDICES["CROTCH"],           # Crotch bottom
                     SMPLX_LANDMARK_INDICES["BACK_WAISTBAND"]    # Belly button back
                    ),
                "out_seam_length":
                    (SMPLX_LANDMARK_INDICES["LEFT_WAIST_SIDE"],
                     SMPLX_LANDMARK_INDICES["LEFT_HEEL"]
                    ),
               }

    # defined with landmarks and joints
    # landmarks are defined with indices of the smpl model points
    # normals are defined with joint names of the smpl model
    CIRCUMFERENCES = {
        "neck":{"LANDMARKS":["NECK_ADAM_APPLE"],
                "JOINTS":["spine1","spine3"]},
        "full_chest_horizontal":{"LANDMARKS":["LEFT_NIPPLE","RIGHT_NIPPLE"],
                                 "JOINTS":["pelvis","spine3"]},
        "full_stomach_horizontal":{"LANDMARKS":["BELLY_BUTTON","BACK_BELLY_BUTTON"],
                                   "JOINTS":["pelvis","spine3"]},
        "waist_width":{"LANDMARKS":["FRONT_STOMACH","BACK_STOMACH"],
                       "JOINTS":["pelvis","spine3"]},
        "hips_seat_width":{"LANDMARKS":["PUBIC_BONE"],
                           "JOINTS":["pelvis","spine3"]},
        "wrist_width_cuff":{"LANDMARKS":["RIGHT_WRIST"],
                            "JOINTS":["right_wrist","right_elbow"]},
        "biceps":{"LANDMARKS":["RIGHT_BICEP"],
                  "JOINTS":["right_shoulder","right_elbow"]},
        "forearms":{"LANDMARKS":["RIGHT_FOREARM"],
                    "JOINTS":["right_elbow","right_wrist"]},
        "thigh_width":{"LANDMARKS":["LEFT_THIGH"],
                       "JOINTS":["pelvis","spine3"]},
        "calf_width":{"LANDMARKS":["LEFT_CALF"],
                      "JOINTS":["pelvis","spine3"]},
        "leg_opening_leg_bottom":{"LANDMARKS":["LEFT_ANKLE","LEFT_HEEL"],
                                   "JOINTS":["left_ankle","left_foot"]},
        "knee_width":{"LANDMARKS":["RIGHT_KNEE"],
                      "JOINTS":["pelvis","spine3"]},
                    
                    }
    
    possible_measurements = list(LENGTHS.keys()) + list(CIRCUMFERENCES.keys())

    CIRCUMFERENCE_TO_BODYPARTS = {
        "neck":"neck",
        "full_chest_horizontal":["spine1","spine2"],
        "full_stomach_horizontal":["hips","spine"],
        "waist_width":["hips","spine"],
        "hips_seat_width":"hips",
        "wrist_width_cuff":["rightHand","rightForeArm"],
        "biceps":"rightArm",
        "forearms":"rightForeArm",
        "thigh_width": "leftUpLeg",
        "calf_width": "leftLeg",
        "leg_opening_leg_bottom": ["leftLeg","leftFoot"],
        "knee_width": ["rightUpLeg", "rightLeg"],
    }