from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import predict_image
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ImageRequest(BaseModel):
    image_path: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ML Skin Disease Classification"}

@app.post("/predict")
async def predict(request: ImageRequest):
    """
    Predict skin disease from image
    
    Request:
        image_path: str - Path to the image file
    
    Response:
        {
            "prediction": str,
            "prediction_full_name": str,
            "confidence": float,
            "top_k": [
                {"label": str, "full_name": str, "confidence": float}
            ],
            "warning": str
        }
    """
    logger.info(f"Received prediction request for: {request.image_path}")
    
    # Validate file exists
    if not os.path.exists(request.image_path):
        logger.error(f"Image file not found: {request.image_path}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Image file not found",
                "path": request.image_path
            }
        )
    
    # Run prediction
    try:
        result = predict_image(
            image_path=request.image_path,
            top_k=3,
            confidence_threshold=0.6
        )
        
        # Check for errors in result
        if "error" in result:
            logger.error(f"Prediction error: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=result
            )
        
        logger.info(f"Prediction successful: {result['prediction']} ({result['confidence']})")
        return result
        
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
    logger.info("Starting ML Service on http://127.0.0.1:8000")
    logger.info("Model will be loaded on first prediction request")
    uvicorn.run(app, host="127.0.0.1", port=8000)
