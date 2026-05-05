# 🚀 Training/Inference Alignment - Action Plan

## 📋 What's Been Completed

### ✅ Phase 1: Infrastructure Setup
- [x] TensorFlow training pipeline (`train_tensorflow.py`)
- [x] TensorFlow inference module (`model_tensorflow.py`)
- [x] Dataset preparation utility (`prepare_dataset.py`)
- [x] Backend model switching (`model_switcher.py`)
- [x] Enhanced logging at each step

### ✅ Phase 2: Alignment Verification Framework
- [x] **test_inference.py** - Comprehensive alignment testing
  - Tests 1: Preprocessing matches training exactly
  - Test 2: Model predictions are generated
  - Test 3: Confidence analysis on training images
  - Test 4: Batch processing compatibility
  - Test 5: Recommendations for improvement

- [x] **ALIGNMENT_GUIDE.md** - Complete reference
  - Critical alignment points explained
  - Training vs inference comparison
  - Debugging checklist
  - Quick reference commands

- [x] **run_pipeline.py** - Interactive setup assistant
  - Validates prerequisites
  - Runs steps in correct order
  - Guides user through entire pipeline

### ✅ Phase 3: Model Preprocessing Enhancement
- [x] Updated `model_tensorflow.py` preprocessing
  - Detailed step-by-step logging (7 steps)
  - Raw prediction output for debugging
  - Exact match with training pipeline

---

## 🎯 Your Next Steps (In Order)

### Step 1: Verify Dataset Exists ⏱️ ~1 minute
```bash
# Check if HAM10000 dataset is in place
ls -la ../backend/data/

# You should see:
# - HAM10000_metadata.csv
# - HAM10000_images_part_1/
# - HAM10000_images_part_2/
```

**If missing:** Download from https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000

### Step 2: Prepare Dataset ⏱️ ~2-5 minutes
```bash
cd ml-service
python prepare_dataset.py
```

**What it does:**
- Loads HAM10000 metadata
- Verifies all images exist
- Splits into train/val by disease class (80/20)
- Creates directory structure: `train/class/image.jpg`
- Shows statistics: images per class

**Expected output:**
```
✓ Images found: 10015
✓ Training set: 8012 images (8 per class per disease)
✓ Validation set: 2003 images (2 per class per disease)
✓ Class distribution balanced
```

### Step 3: Train Model ⏱️ ~10-30 minutes (depends on GPU)
```bash
python train_tensorflow.py
```

**What it does:**
- Loads training data with augmentation
- Creates ResNet50 transfer learning model
- Fine-tunes with EarlyStopping
- Prints class indices at start
- Saves model as `model_tensorflow.h5`
- Saves class indices to `../backend/model/class_indices.json`

**Expected output:**
```
STEP 1: Setup ✓
STEP 2: Load Data ✓
Class indices: {0: 'akiec', 1: 'bcc', ...}
STEP 3: Build Model ✓
Model loaded successfully
STEP 4: Train ✓
Epoch 1/50 - loss: 1.234 - accuracy: 0.756 - val_loss: 0.567 - val_accuracy: 0.821
...
Epoch 35/50 - Training complete!
STEP 5: Save ✓
Model saved to model_tensorflow.h5 (92 MB)
Class indices saved
```

### Step 4: Validate Training ⏱️ ~2 minutes
```bash
python validate_training.py
```

**What it does:**
- Checks class indices file exists and is correct
- Verifies model file saved properly
- Analyzes training data structure
- Checks dataset balance
- Recommends improvements

**Expected output:**
```
✓ Class indices loaded: 7 classes
✓ Model file exists: 92 MB
✓ Training data: 8012 images in train/
✓ Validation data: 2003 images in val/
✓ Dataset balanced: ±2% class distribution
```

### Step 5: Test Inference ⏱️ ~3-5 minutes
```bash
python test_inference.py
```

**What it does:**
- Loads model and class indices
- Tests preprocessing pipeline
- Makes predictions on training images
- Verifies confidence > 80%
- Tests batch processing
- Provides recommendations

**Expected output:**
```
✓ Prerequisites met
✓ Model loaded
✓ Image loaded and preprocessed
✓ Predictions: akiec=95.2%, bcc=2.1%, ...
✓ MODEL IS CORRECT! (95.2% confidence)
✓ HIGH CONFIDENCE (>80%)
✓ Batch processing works (50/50 correct in batch)
```

---

## 📊 Success Criteria

Your system is **ALIGNED** when:

| Criterion | Target | How to Verify |
|-----------|--------|---------------|
| Preprocessing | Matches | `test_inference.py` TEST 1 passes |
| Model predictions | Generated | `test_inference.py` TEST 2 passes |
| Confidence | >80% on training | `test_inference.py` TEST 3 shows >80% |
| Batch processing | Works | `test_inference.py` TEST 4 passes |
| Class indices | Match | `validate_training.py` checks match |
| Same predictions | For same image | Run twice on same image |

---

## 🔧 Troubleshooting

### Problem: "No module named tensorflow"
```bash
pip install tensorflow
```

### Problem: "Out of memory during training"
- Edit `train_tensorflow.py`
- Change `BATCH_SIZE = 32` to `BATCH_SIZE = 16`
- Reduce `EPOCHS` from 50 to 30

### Problem: "Model confidence < 50%"
- Run: `python test_inference.py`
- Check what's wrong
- If preprocessing wrong: Fix `model_tensorflow.py` preprocess_image()
- If model not trained: Re-run `python train_tensorflow.py`

### Problem: "Class indices don't match"
- Delete: `../backend/model/class_indices.json`
- Re-run: `python train_tensorflow.py`

---

## 📁 Quick File Reference

```
ml-service/
├── train_tensorflow.py           ← Run this SECOND (training)
├── model_tensorflow.py           ← Inference - preprocesses + predicts
├── prepare_dataset.py            ← Run this FIRST (organize data)
├── validate_training.py          ← Run this THIRD (verify setup)
├── test_inference.py             ← Run this FOURTH (test alignment)
├── model_switcher.py             ← Backend integration
├── run_pipeline.py               ← Interactive guide
├── model_tensorflow.h5           ← GENERATED: Trained model
├── training_history.json         ← GENERATED: Training metrics
├── ALIGNMENT_GUIDE.md            ← Reference documentation
└── README_TENSORFLOW.md          ← Full setup guide

backend/model/
└── class_indices.json            ← GENERATED: Class mapping
```

---

## ⚡ Quick Commands

```bash
# Prepare dataset (must do first)
python prepare_dataset.py

# Train model (must do second)
python train_tensorflow.py

# Validate setup (optional but recommended)
python validate_training.py

# Test inference (to verify >80% confidence)
python test_inference.py

# Run full pipeline interactively
python run_pipeline.py

# Test on specific image (after training)
python model_switcher.py test /path/to/image.jpg

# Check current backend
python model_switcher.py status

# Switch to TensorFlow
python model_switcher.py set-tensorflow

# Switch to PyTorch
python model_switcher.py set-pytorch
```

---

## 📈 Expected Timeline

| Step | Duration | Command |
|------|----------|---------|
| 1. Verify dataset | 1 min | `ls -la ../backend/data/` |
| 2. Prepare dataset | 3 min | `python prepare_dataset.py` |
| 3. Train model | 20 min | `python train_tensorflow.py` |
| 4. Validate | 2 min | `python validate_training.py` |
| 5. Test inference | 5 min | `python test_inference.py` |
| **Total** | **31 min** | - |

---

## ✨ Key Alignment Points (CRITICAL)

Your system is aligned when these match between training and inference:

### Image Size
```python
Training: IMG_SIZE = (224, 224)
Inference: load_img(path, target_size=(224, 224))
```

### Rescaling
```python
Training: ImageDataGenerator(rescale=1./255)
Inference: img_array * (1./255)  # Must be exactly this
```

### Class Indices
```python
Training: Saves to ../backend/model/class_indices.json
Inference: Loads from same file
```

### Batch Shape
```python
Training: (batch_size, 224, 224, 3) with values [0, 1]
Inference: (1, 224, 224, 3) with values [0, 1]
```

---

## 🎓 Understanding the System

### Training Pipeline
```
HAM10000 dataset
    ↓
prepare_dataset.py (80/20 split)
    ↓
train/
├── akiec/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── bcc/
└── ...
    ↓
ImageDataGenerator(rescale=1./255)
    ↓
ResNet50 + Dense layers
    ↓
Training 50 epochs
    ↓
model_tensorflow.h5 + class_indices.json
```

### Inference Pipeline
```
User uploads image
    ↓
Backend receives (multipart/form-data)
    ↓
model_tensorflow.py:preprocess_image()
    - load_img(target_size=(224,224))
    - img_to_array()
    - * (1./255)  ← MUST MATCH TRAINING
    - expand_dims()
    ↓
model.predict()
    ↓
idx_to_class lookup
    ↓
{"prediction": "melanoma", "confidence": 92.5%, ...}
    ↓
Frontend displays result
```

---

## ✅ Verification Checklist

Before deploying, ensure all are checked:

```
Dataset Preparation:
[ ] HAM10000 files downloaded
[ ] prepare_dataset.py ran successfully
[ ] train/ and val/ directories created
[ ] Class balance verified

Model Training:
[ ] training_tensorflow.py completed
[ ] model_tensorflow.h5 saved (92 MB)
[ ] class_indices.json saved
[ ] Training logs show reasonable accuracy

Alignment Verification:
[ ] validate_training.py shows no errors
[ ] test_inference.py shows >80% confidence
[ ] Predictions correct on training images
[ ] Same image gives same prediction twice

System Integration:
[ ] Model file in correct location
[ ] Class indices in correct location
[ ] Backend can find model file
[ ] No import errors
```

---

## 🚀 After Training is Complete

Once `test_inference.py` shows everything is working (>80% confidence):

### Option 1: Use TensorFlow Model
```python
# In app.py
from model_switcher import predict_with_config
result = predict_with_config(image_path)
```

### Option 2: Deploy as Production Model
```bash
# Copy model to production location
cp model_tensorflow.h5 /path/to/production/
cp ../backend/model/class_indices.json /path/to/production/

# Update app.py to use TensorFlow
python model_switcher.py set-tensorflow

# Restart backend
node server.js
```

### Option 3: A/B Testing
Keep both models running and compare:
```python
pytorch_result = predict_image("image.jpg")  # PyTorch fallback
tensorflow_result = predict_image_tensorflow("image.jpg")  # TensorFlow
# Compare confidence and class
```

---

## 📞 Need Help?

Check these in order:
1. **ALIGNMENT_GUIDE.md** - Detailed reference
2. **test_inference.py output** - Shows exact errors
3. **README_TENSORFLOW.md** - Training guide
4. **run_pipeline.py** - Interactive debugging

Good luck! 🎉
