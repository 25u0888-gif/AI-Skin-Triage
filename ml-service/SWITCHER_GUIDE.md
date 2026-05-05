# Model Switcher Integration Guide

## Overview

The `model_switcher.py` provides an easy way to switch between PyTorch and TensorFlow backends without modifying `app.py`. It uses a configuration file to manage which model to use.

## Quick Start

### Check Current Configuration
```bash
cd ml-service
python model_switcher.py status
```

Output:
```
============================================================
Model Configuration Status
============================================================
Current Backend: PYTORCH
PyTorch Model: model.pth
  - Exists: False
  - Fallback: True

TensorFlow Model: model_tensorflow.h5
  - Exists: False

Settings:
  - Confidence Threshold: 0.6
  - Top-K Predictions: 3
============================================================
```

### Switch to PyTorch
```bash
python model_switcher.py set-pytorch
```

### Switch to TensorFlow
```bash
python model_switcher.py set-tensorflow
```

### Test a Prediction
```bash
python model_switcher.py test /path/to/image.jpg
```

## Integration with Backend

### Option 1: Use in app.py (FastAPI)

Replace the current import in `app.py`:

```python
# OLD (direct import):
# from model import predict_image

# NEW (using switcher):
from model_switcher import predict_with_config

@app.post("/predict")
async def predict(request: ImageRequest):
    """Use configured backend for prediction"""
    result = predict_with_config(request.image_path)
    
    if "error" in result:
        raise HTTPException(
            status_code=500,
            detail=result
        )
    
    return result
```

### Option 2: Manual Backend Selection

```python
from model_switcher import set_backend, get_predictor

# Switch backend
set_backend("tensorflow")

# Get the predictor function
predict_func = get_predictor()

# Use it
result = predict_func(image_path)
```

## Configuration File (model_config.json)

The switcher creates a `model_config.json` file:

```json
{
  "backend": "pytorch",
  "pytorch_model": "model.pth",
  "tensorflow_model": "model_tensorflow.h5",
  "fallback_mode": true,
  "confidence_threshold": 0.6,
  "top_k": 3
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backend` | string | "pytorch" | Which backend to use: "pytorch" or "tensorflow" |
| `pytorch_model` | string | "model.pth" | Path to PyTorch model file |
| `tensorflow_model` | string | "model_tensorflow.h5" | Path to TensorFlow model file |
| `fallback_mode` | bool | true | Use fallback predictions if model unavailable |
| `confidence_threshold` | float | 0.6 | Minimum confidence for prediction |
| `top_k` | int | 3 | Number of top predictions to return |

### Manual Configuration

Edit `model_config.json` directly:

```json
{
  "backend": "tensorflow",
  "tensorflow_model": "models/skin_disease_v2.h5",
  "confidence_threshold": 0.7,
  "top_k": 5
}
```

## Workflow Examples

### Example 1: Development (PyTorch with Fallback)
```bash
# Check status
python model_switcher.py status

# Use fallback predictions
python model_switcher.py set-pytorch

# app.py will automatically use PyTorch with fallback
```

### Example 2: Training & Testing (TensorFlow)
```bash
# Prepare dataset
python prepare_dataset.py

# Train new model
python train_tensorflow.py
# Saves to: model_tensorflow.h5

# Switch backend
python model_switcher.py set-tensorflow

# Test prediction
python model_switcher.py test ../backend/uploads/test_image.jpg

# Backend automatically uses TensorFlow
```

### Example 3: Production (Best Model)
```bash
# Option 1: Use trained PyTorch model
python model_switcher.py set-pytorch
# Place trained model.pth in ml-service/

# Option 2: Use trained TensorFlow model  
python model_switcher.py set-tensorflow
# Place trained model_tensorflow.h5 in ml-service/

# Option 3: Ensemble (coming soon)
# Would check both models and use best prediction
```

## Full Integration Example for app.py

Here's a complete example of integrating the switcher into your FastAPI app:

```python
# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from model_switcher import predict_with_config, load_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ImageRequest(BaseModel):
    image_path: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    config = load_config()
    return {
        "status": "healthy",
        "service": "ML Skin Disease Classification",
        "backend": config["backend"]
    }

@app.get("/config")
async def get_config():
    """Get current model configuration"""
    config = load_config()
    return config

@app.post("/config")
async def update_config(config: dict):
    """Update model configuration"""
    from model_switcher import save_config, initialize_config
    
    # Load current config
    current = load_config()
    
    # Update with new values
    current.update(config)
    
    # Save and validate
    save_config(current)
    
    return {
        "status": "updated",
        "config": current
    }

@app.post("/predict")
async def predict(request: ImageRequest):
    """
    Predict skin disease using configured backend
    
    Request:
        image_path: str - Path to the image file
    
    Response:
        {
            "prediction": str,
            "confidence": float,
            "top_k": [...]
        }
    """
    logger.info(f"Received prediction request for: {request.image_path}")
    
    # Validate file exists
    if not os.path.exists(request.image_path):
        logger.error(f"Image file not found: {request.image_path}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Image file not found"}
        )
    
    # Get prediction using configured backend
    try:
        result = predict_with_config(request.image_path)
        
        # Check for errors
        if "error" in result:
            logger.error(f"Prediction error: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=result
            )
        
        logger.info(f"Prediction successful: {result['prediction']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception during prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Prediction failed: {str(e)}",
                "warning": "This is an AI-assisted prediction and not a medical diagnosis."
            }
        )

if __name__ == "__main__":
    import uvicorn
    config = load_config()
    logger.info(f"Starting ML Service with {config['backend']} backend")
    logger.info(f"Model will be loaded on first prediction request")
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## Troubleshooting

### Model Not Found Error
```bash
# Check what models are available
ls -la ml-service/model*

# Check config
python model_switcher.py status

# If model doesn't exist, either:
# 1. Train it (for TensorFlow)
# 2. Use fallback mode (PyTorch)
# 3. Update path in model_config.json
```

### Backend Not Switching
```bash
# Verify config file was updated
cat ml-service/model_config.json

# Restart the backend service
# (Changes take effect on next request)
```

### Fallback Mode Active
```bash
# This is expected if model files don't exist
# The system will generate realistic random predictions
# To use trained models:

# 1. For PyTorch: place model.pth in ml-service/
# 2. For TensorFlow: run train_tensorflow.py or place model_tensorflow.h5 in ml-service/
```

## Advanced Usage

### Programmatic Backend Switching

```python
from model_switcher import set_backend, predict_with_config

# Switch backends on the fly
set_backend("pytorch")
result1 = predict_with_config("image1.jpg")

set_backend("tensorflow")
result2 = predict_with_config("image2.jpg")

# Compare results
print(f"PyTorch: {result1['prediction']} ({result1['confidence']})")
print(f"TensorFlow: {result2['prediction']} ({result2['confidence']})")
```

### Ensemble Predictions (Future)

```python
def ensemble_predict(image_path):
    """Average predictions from both models"""
    set_backend("pytorch")
    result1 = predict_with_config(image_path)
    
    set_backend("tensorflow")
    result2 = predict_with_config(image_path)
    
    # Average the confidence scores
    avg_conf = (result1['confidence'] + result2['confidence']) / 2
    
    return {
        "prediction": result1['prediction'],
        "confidence": avg_conf,
        "ensemble": True
    }
```

## Summary

| Aspect | Details |
|--------|---------|
| Config File | `ml-service/model_config.json` |
| Switch Backend | `python model_switcher.py set-{pytorch\|tensorflow}` |
| Check Status | `python model_switcher.py status` |
| Test Model | `python model_switcher.py test image.jpg` |
| Integration | Update `app.py` to use `predict_with_config()` |
| Fallback | Automatic if model file doesn't exist |

