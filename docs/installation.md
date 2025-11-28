# Installation Guide

Follow these steps to run the ROMP Pipeline API locally or on a server.

---

## 1. Prerequisites
- Python 3.8+
- Git
- `pip`
- PyTorch 1.10+ (matching your CUDA/CPU environment)
- `simple-romp` (provides the `romp` CLI)
- SMPL models from [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de/)

GPU acceleration is recommended; CPU works but is slower.

---

## 2. Clone and create an environment
```bash
git clone https://github.com/yourusername/romp-pipeline.git
cd romp-pipeline  (This is the optional way)

python3.8 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

---

## 3. Install dependencies
```bash
# Build prerequisites required before installing smplx/simple-romp
pip install numpy Cython wheel setuptools smplx smpl

# PyTorch and torchvision (choose appropriate CUDA build)
pip install torch torchvision

#Install simple-romp explicitly if not bundled
pip install simple-romp

# ROMP Pipeline itself
pip install -e .
```

---

## 4. Populate the `data/` directory with ROMP assets
Full ROMP/SMPL measurement support needs asset files that are not bundled with `pip install -e .`.

### 4.1 Download ROMP metadata bundle
- **Source:** [`smpl_model_data.zip`](https://github.com/Arthur151/ROMP/releases/download/V2.0/smpl_model_data.zip)
- **Purpose:** Provides the folder structure plus helper matrices shipped with the ROMP project.

Steps:
```bash
mkdir -p data
wget -O /tmp/smpl_model_data.zip \
  https://github.com/Arthur151/ROMP/releases/download/V2.0/smpl_model_data.zip
unzip -q /tmp/smpl_model_data.zip -d data
mv data/smpl_model_data data/smpl_models
```
Unzipping the archive yields a folder named `smpl_model_data` that already contains a `smpl/` subdirectory and the helper `.npy` assets referenced below. Move or rename that folder to `data/smpl_models` so the pipeline can discover it. Manual extraction via your OS file manager works equally well.

### 4.2 Register and add the official SMPL model
- **Source:** [smpl.is.tue.mpg.de](https://smpl.is.tue.mpg.de/)
- **File needed:** `SMPL_NEUTRAL.pkl` from “Download version 1.1.0 for Python 2.7 (female/male/neutral, 300 shape PCs)”

Steps:
1. Create an account on the SMPL website, agree to the license, and download the v1.1.0 Python package.
2. Extract the archive locally. Inside the release you will find the `SMPL_NEUTRAL.pkl`.
3. Copy `SMPL_NEUTRAL.pkl` into `data/smpl_models/smpl/` (this path corresponds to the `smpl_model_data/smpl` folder you just unpacked; overwrite if prompted so the official file replaces the ROMP placeholder).

> The SMPL license forbids redistributing the `.pkl` files. Keep your download safely stored so you can redeploy later.

### 4.3 ROMP helper matrices (`data/smpl_models/`)
- **Source:** [Arthur151/ROMP – `data/model_data`](https://github.com/Arthur151/ROMP/tree/master/data/model_data)
- **Files required:** `J_regressor_extra.npy`, `J_regressor_h36m.npy`, `smpl_kid_template.npy`

If you extracted `smpl_model_data.zip`, the helper matrices are already in the `smpl_model_data` folder you copied.

### 4.4 Anthropometry segmentation (`data/body_measurements/`)
- **Source:** [DavidBoja/SMPL-Anthropometry – `body_measurements/smpl`](https://github.com/DavidBoja/SMPL-Anthropometry/tree/master/body_measurements/smpl)
- **File required:** `smpl_body_parts_2_faces.json`

```bash
mkdir -p data/body_measurements/smpl
wget -O data/body_measurements/smpl/smpl_body_parts_2_faces.json \
  https://github.com/DavidBoja/SMPL-Anthropometry/blob/master/data/smpl/smpl_body_parts_2_faces.json
```
This JSON powers the segmentation lookup used by `MeasureBody`. Download it once and keep it under `data/body_measurements/smpl/`.

After these downloads, your tree should look like:
```
data/
├── body_measurements/
│   └── smpl/
│       └── smpl_body_parts_2_faces.json
└── smpl_models/
    ├── J_regressor_extra.npy
    ├── J_regressor_h36m.npy
    ├── smpl/
    │   ├── SMPL_FEMALE.pkl
    │   ├── SMPL_MALE.pkl
    │   └── SMPL_NEUTRAL.pkl
    └── smpl_kid_template.npy
```

---

## 5. Verify installation
```bash
romp --help                 # ROMP CLI reachable
romp-api --help             # Entry point installed
python -c "from romp_pipeline import MeasureBody; print('OK')"
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

If any step fails, revisit the previous sections or reinstall the missing dependency.

---

## 6. Next steps
- [Start the API](api_usage.md#starting-the-server)
- [Understand the architecture](api_architecture.md)
- [Read measurement implementation notes](crotch_measurement_fix.md)
