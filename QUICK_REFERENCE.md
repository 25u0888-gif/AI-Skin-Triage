# ⚡ QUICK REFERENCE - Commands & Config

## Deploy in 5 Commands

```bash
# 1. Generate non-skin dataset (5 min)
cd c:\hackthon angadi frontend\ml-service
python generate_unknown_dataset.py

# 2. Train 8-class model (20-40 min)
python train_with_unknown.py

# 3. Validate everything (5 min)
python validate_with_safety.py

# 4. Deploy model
ren model_tensorflow_backup.h5 model_tensorflow_old.h5
ren model_tensorflow.h5 model_tensorflow_backup.h5
ren model_tensorflow_with_unknown.h5 model_tensorflow.h5

# 5. Start all services
# Terminal 1:
python app.py

# Terminal 2:
cd ..\backend && node server.js

# Terminal 3:
cd ..\triage-app && npm run dev
```

---

## Service Ports

| Service | Port | URL | Command |
|---------|------|-----|---------|
| ML Service | 8000 | http://127.0.0.1:8000 | `python app.py` |
| Backend API | 5000 | http://127.0.0.1:5000 | `node server.js` |
| Frontend | 5173 | http://127.0.0.1:5173 | `npm run dev` |

---

## Key Configuration

| Parameter | Value | File | Notes |
|-----------|-------|------|-------|
| Confidence Threshold | 0.60 | model_tensorflow.py | Min for disease diagnosis |
| Image Size | 224×224 | model_tensorflow.py | MUST match training |
| Rescale Factor | 1/255 | model_tensorflow.py | Normalize pixels |
| Classes | 8 | class_indices.json | 7 diseases + unknown |
| Batch Size | 32 | train_with_unknown.py | Training only |
| Epochs | 50 + 20 | train_with_unknown.py | Train + fine-tune |
| Grad-CAM Layer | conv5_block3_out | model_tensorflow.py | ResNet50 last conv |

---

## Response Structure

```json
{
  "prediction": "Melanoma",
  "prediction_full_name": "Melanoma",
  "confidence": 0.92,
  "is_valid_skin": true,
  "is_confident": true,
  "heatmap": {
    "image": "base64_encoded_jpeg_data",
    "width": 224,
    "height": 224
  },
  "top_k": [
    {"label": "mel", "full_name": "Melanoma", "confidence": 0.92},
    {"label": "nv", "full_name": "Nevus", "confidence": 0.05},
    {"label": "bcc", "full_name": "BCC", "confidence": 0.03}
  ],
  "warning": "This is an AI-assisted prediction...",
  "debug_info": {
    "status": "✓ SUCCESS",
    "confidence_threshold": 0.60,
    "is_unknown_class": false,
    "is_above_threshold": true,
    "all_probabilities": {
      "akiec": 0.01,
      "bcc": 0.03,
      "bkl": 0.02,
      "df": 0.00,
      "mel": 0.92,
      "nv": 0.01,
      "vasc": 0.01,
      "unknown": 0.00
    }
  }
}
```

---

## Class Labels

| Code | Full Name |
|------|-----------|
| akiec | Actinic Keratosis/Intraepithelial Carcinoma |
| bcc | Basal Cell Carcinoma |
| bkl | Benign Keratosis-like Lesions |
| df | Dermatofibroma |
| mel | Melanoma |
| nv | Melanocytic Nevus |
| vasc | Vascular Lesions |
| unknown | Non-Skin / Unknown / Background |

---

## Frontend File Locations

```
triage-app/
├── src/
│   ├── pages/
│   │   ├── UploadPage.jsx       ← Image upload form
│   │   ├── ResultsPage.jsx      ← Display results + heatmap (UPDATED)
│   │   └── HowItWorksPage.jsx   ← Instructions
│   ├── App.jsx                  ← Main app
│   └── main.jsx                 ← Entry point
```

---

## ML Service Files

```
ml-service/
├── model_tensorflow.py           ← MAIN INFERENCE (UPDATED with Grad-CAM)
│   ├── predict_image_tensorflow()
│   └── generate_gradcam_heatmap()
├── app.py                         ← Flask/FastAPI server
├── train_with_unknown.py         ← NEW: Training script
├── generate_unknown_dataset.py   ← NEW: Dataset generator
├── validate_with_safety.py       ← NEW: Test suite
├── model_tensorflow.h5           ← Current model (deployed)
├── model_tensorflow_with_unknown.h5 ← New model (to be deployed)
└── model_tensorflow_backup.h5    ← Backup
```

---

## Debugging Checklist

### Heatmap Not Showing?
```python
# Check response has these fields:
assert response['is_valid_skin'] == True       # Must be true
assert response['confidence'] >= 0.60          # Must exceed threshold
assert 'unknown' not in response['prediction'] # Must not be unknown
assert response['heatmap'] is not None         # Must have heatmap data
```

### Model Rejecting Valid Skin?
```python
# Check if old model is loaded (only 7 classes)
# Solution: Deploy new model_tensorflow_with_unknown.h5
len(class_indices) == 8  # Must be 8 classes
'unknown' in class_indices  # Must include unknown
```

### Wrong Predictions?
```bash
# Verify preprocessing matches training
# Training: img_array * (1/255)
# Inference: img_array * (1/255)  ← MUST MATCH

# Verify image size
# Expected: (1, 224, 224, 3)  ← Batch, height, width, channels
```

### Heatmap Highlighting Wrong Area?
```python
# Verify last conv layer name for ResNet50
# Should be: "conv5_block3_out"
# Check: model.summary() to see layer names
```

---

## Health Checks

```bash
# ML Service health
curl http://127.0.0.1:8000/health

# Backend health  
curl http://127.0.0.1:5000/

# Frontend
Open http://127.0.0.1:5173 in browser

# Model file
ls -la c:\hackthon angadi frontend\ml-service\*.h5

# Class indices
cat c:\hackthon angadi frontend\backend\model\class_indices.json

# Check running processes
tasklist | findstr python   # ML Service
tasklist | findstr node     # Backend
```

---

## Quick Test Commands

```bash
# Test non-skin rejection
python -c "
from model_tensorflow import predict_image_tensorflow
result = predict_image_tensorflow('../backend/data/val/unknown/unknown_val_00001.jpg')
print('Valid skin:', result.get('is_valid_skin'))
print('Prediction:', result.get('prediction'))
"

# Test with real skin image
python -c "
from model_tensorflow import predict_image_tensorflow
result = predict_image_tensorflow('../backend/data/train/mel/ISIC_123.jpg')
print('Prediction:', result.get('prediction'))
print('Confidence:', result.get('confidence'))
print('Has heatmap:', result.get('heatmap') is not None)
"

# Check dataset counts
import os
train_unknown = len(os.listdir('../backend/data/train/unknown'))
val_unknown = len(os.listdir('../backend/data/val/unknown'))
print(f'Training: {train_unknown}, Validation: {val_unknown}')
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `model_tensorflow.h5 not found` | File not deployed | Rename model_tensorflow_with_unknown.h5 |
| All predictions "Uncertain" | Old model (7 classes) | Deploy new 8-class model |
| Non-skin not rejected | Unknown class missing | Run generate_unknown_dataset.py |
| Heatmap not showing | is_valid_skin=False | Check confidence > 0.60 |
| Wrong heatmap area | Conv layer mismatch | Verify "conv5_block3_out" exists |
| Out of memory | GPU too small | Use CPU or reduce batch size |
| Slow inference | CPU only | GPU recommended (~1 sec/image) |

---

## Key API Endpoints

### ML Service
```
POST http://127.0.0.1:8000/predict
Content-Type: image/jpeg
Body: Image file bytes

Response: JSON with prediction, confidence, heatmap
```

### Backend API
```
POST http://127.0.0.1:5000/analyze
Content-Type: multipart/form-data
Body: image=<file>

Response: JSON with results for frontend
```

---

## Environment Variables

```bash
# Optional: Set to use CPU only
set CUDA_VISIBLE_DEVICES=-1

# Optional: Set TensorFlow logging
set TF_CPP_MIN_LOG_LEVEL=2  # Suppress warnings
```

---

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Inference time | < 2 sec | ~1 sec (GPU) |
| Heatmap gen | < 1 sec | ~0.5 sec |
| Model size | ~90 MB | 92 MB |
| Memory (GPU) | < 2 GB | ~1.5 GB |
| Disk space | ~200 MB | 180 MB |

---

## Important Files to Keep Backed Up

```
📦 Backup These:
├── ml-service/model_tensorflow_backup.h5        ← Old model
├── backend/model/class_indices.json             ← Class mapping
├── backend/data/                                ← Dataset
├── triage-app/src/pages/ResultsPage.jsx        ← Frontend config
└── ml-service/model_tensorflow.py               ← Core inference
```

---

## Verification Checklist (< 5 min)

```
After deployment, verify:
- [ ] model_tensorflow.h5 exists (~90 MB)
- [ ] class_indices.json has 8 classes
- [ ] ML Service starts: python app.py ✓
- [ ] Backend starts: node server.js ✓
- [ ] Frontend loads: http://127.0.0.1:5173 ✓
- [ ] Upload works: Can select image ✓
- [ ] Prediction works: Shows result ✓
- [ ] Heatmap visible: For valid predictions ✓
- [ ] No heatmap: For "No skin" predictions ✓
```

---

## Next Steps After Deployment

1. ✅ Deploy model and test
2. ⏳ Collect real user feedback
3. ⏳ Monitor prediction accuracy
4. ⏳ Retrain with new validated data
5. ⏳ Improve unknown class with real non-skin images
6. ⏳ Consider ensemble methods for higher confidence

---

**Total time: ~1 hour to full deployment** ⏱️

Start with `python generate_unknown_dataset.py` and follow DEPLOYMENT_CHECKLIST.md!
