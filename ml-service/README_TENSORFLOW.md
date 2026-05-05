# TensorFlow Training & Inference for HAM10000

This directory contains alternative TensorFlow-based training and inference scripts for the skin disease classification system.

## Files

- **train_tensorflow.py** - Complete training script using TensorFlow/Keras with transfer learning
- **model_tensorflow.py** - Inference module for TensorFlow trained models
- **model.py** - Current PyTorch inference (keep as backup)

## Quick Start

### Option 1: Use PyTorch (Current Setup - Recommended)

The system is currently configured to use PyTorch for inference. The fallback mode generates realistic random predictions for testing.

```bash
# No additional setup needed - system is ready to use
cd ml-service
python app.py
```

### Option 2: Train with TensorFlow

If you want to train a new model using TensorFlow with the HAM10000 dataset:

#### Step 1: Install TensorFlow

```bash
pip install tensorflow tensorflow-io opencv-python pillow
```

#### Step 2: Prepare Dataset

Organize your dataset as follows:
```
data/
├── train/
│   ├── akiec/
│   ├── bcc/
│   ├── bkl/
│   ├── df/
│   ├── mel/
│   ├── nv/
│   └── vasc/
└── val/
    ├── akiec/
    ├── bcc/
    ├── bkl/
    ├── df/
    ├── mel/
    ├── nv/
    └── vasc/
```

**Split dataset script** (optional):
```python
import os
import shutil
from sklearn.model_selection import train_test_split

source_dir = "data/HAM10000_images_part_1"
train_dir = "data/train"
val_dir = "data/val"

# Create directories for each class
classes = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

for cls in classes:
    os.makedirs(f"{train_dir}/{cls}", exist_ok=True)
    os.makedirs(f"{val_dir}/{cls}", exist_ok=True)

# Split images by class
metadata = pd.read_csv("data/HAM10000_metadata.csv")
for cls in classes:
    images = metadata[metadata['dx'] == cls]['image_id'].tolist()
    train_imgs, val_imgs = train_test_split(images, test_size=0.2)
    
    # Copy to train
    for img_id in train_imgs:
        src = f"{source_dir}/{img_id}.jpg"
        dst = f"{train_dir}/{cls}/{img_id}.jpg"
        if os.path.exists(src):
            shutil.copy(src, dst)
    
    # Copy to val
    for img_id in val_imgs:
        src = f"{source_dir}/{img_id}.jpg"
        dst = f"{val_dir}/{cls}/{img_id}.jpg"
        if os.path.exists(src):
            shutil.copy(src, dst)
```

#### Step 3: Run Training

```bash
cd ml-service
python train_tensorflow.py
```

**What it does:**
- Loads HAM10000 dataset with data augmentation
- Uses ResNet50 transfer learning (ImageNet pre-trained)
- Trains with early stopping and learning rate reduction
- Fine-tunes the last 50 layers
- Saves best model as `model_tensorflow.h5`
- Saves training history and class indices

**Training output:**
- `model_tensorflow.h5` - Trained model (ResNet50 backbone + custom layers)
- `training_history.json` - Loss/accuracy curves
- `../backend/model/class_indices.json` - Class mapping

#### Step 4: Use TensorFlow Model for Inference

**Option A: Test with inference script**
```bash
cd ml-service
python -c "from model_tensorflow import predict_image_tensorflow; result = predict_image_tensorflow('test_image.jpg'); print(result)"
```

**Option B: Update backend to use TensorFlow**

Edit `app.py` to use the TensorFlow inference:

```python
# In app.py, replace the predict_image import:

# Old (PyTorch):
# from model import predict_image

# New (TensorFlow):
from model_tensorflow import predict_image_tensorflow as predict_image

@app.post("/predict")
async def predict(request: ImageRequest):
    result = predict_image(request.image_path)
    return result
```

Then restart the backend:
```bash
cd backend
node server.js
```

## Model Architecture

### TensorFlow Model
```
Input: (224, 224, 3)
    ↓
ResNet50 (pre-trained on ImageNet, frozen)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512, relu) → Dropout(0.5)
    ↓
Dense(256, relu) → Dropout(0.3)
    ↓
Dense(7, softmax)  ← Output probabilities
```

### PyTorch Model
```
Input: (224, 224, 3)
    ↓
ResNet18 (custom)
    ↓
Linear(512, 7)  ← Output logits + softmax
```

## Performance Comparison

| Metric | PyTorch | TensorFlow |
|--------|---------|-----------|
| Model Size | ~44 MB | ~92 MB |
| Training Speed | Fast | Moderate |
| Inference Speed | Very Fast | Fast |
| Framework | PyTorch | TensorFlow/Keras |

## Troubleshooting

### TensorFlow Memory Issues
If training runs out of GPU memory:
```python
# In train_tensorflow.py, reduce BATCH_SIZE:
BATCH_SIZE = 16  # or 8
```

### Model Not Saving
Check that directories exist:
```bash
mkdir -p ../backend/model
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install tensorflow tensorflow-io opencv-python pillow numpy
```

## Architecture Comparison

### Why Use TensorFlow?
- ✅ Larger, more powerful model (ResNet50 vs ResNet18)
- ✅ Better performance with proper training data
- ✅ Keras API is user-friendly
- ✅ Better integrated with cloud deployment (TF Lite, TF JS)
- ❌ Slower inference
- ❌ Larger model size

### Why Use PyTorch (Current)?
- ✅ Faster inference
- ✅ Smaller model
- ✅ Better for research
- ✅ Simpler to modify
- ❌ Needs more manual configuration
- ❌ Less integration with production tools

## Next Steps

1. **Option 1**: Keep using current PyTorch setup with fallback predictions
2. **Option 2**: Train TensorFlow model with your HAM10000 dataset
3. **Option 3**: Use both models and switch between them

## Contact

For issues with TensorFlow training:
- Check GPU availability: `nvidia-smi`
- Check CUDA compatibility: `python -c "import tensorflow as tf; print(tf.sysconfig.get_build_info()['cuda_version'])"`
- Review training logs for memory/compatibility issues
