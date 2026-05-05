from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import predict
import os

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load model once at startup to optimize performance."""
    try:
        predict.load_resources()
        print("Model and class indices loaded successfully on startup.")
    except Exception as e:
        print(f"Warning: Failed to load model at startup. Error: {e}")
        print("Please ensure you have run train.py to download the dataset and train the model.")

@app.post("/predict")
async def get_prediction(file: UploadFile = File(...)):
    """
    Endpoint to predict skin disease from an uploaded image.
    Accepts an image file and returns the top 3 predictions with confidence scores.
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an image.")
        
    try:
        contents = await file.read()
        result = predict.predict_image(contents)
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Model or required files are missing: {str(e)}. Have you run train.py?"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during prediction: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Skin Disease Prediction API is running. Send POST requests to /predict."}

if __name__ == "__main__":
    # Run the server with uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
