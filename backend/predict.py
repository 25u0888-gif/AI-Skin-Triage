import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'skin_model.h5')
CLASS_INDICES_PATH = os.path.join(MODEL_DIR, 'class_indices.json')

HUMAN_READABLE_CLASSES = {
    'akiec': 'Actinic keratoses',
    'bcc': 'Basal cell carcinoma',
    'bkl': 'Benign keratosis',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic nevi',
    'vasc': 'Vascular lesions'
}

model = None
classes = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_resources():
    global model, classes
    
    if not os.path.exists(MODEL_PATH):
        # Allow starting backend for testing even without model
        print(f"Warning: Model file not found at {MODEL_PATH}")
        return
        
    if not os.path.exists(CLASS_INDICES_PATH):
        print(f"Warning: Class indices file not found at {CLASS_INDICES_PATH}")
        return
        
    if classes is None:
        with open(CLASS_INDICES_PATH, "r") as f:
            class_indices = json.load(f)
            classes = {int(v): k for k, v in class_indices.items()}
            
    if model is None:
        num_classes = len(classes)
        try:
            model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        except:
            model = models.mobilenet_v2(pretrained=False)
            
        model.classifier[1] = nn.Linear(model.last_channel, num_classes)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model = model.to(device)
        model.eval()

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    img_tensor = transform(img).unsqueeze(0)
    return img_tensor

def predict_image(image_bytes):
    if model is None or classes is None:
        load_resources()
        if model is None:
            # Mock prediction if model is missing to allow testing the UI
            return {
                "prediction": "Melanoma (Mock)",
                "confidence": 0.93,
                "top_3": [
                  {"class": "Melanoma (Mock)", "score": 0.93},
                  {"class": "Nevus (Mock)", "score": 0.04},
                  {"class": "Benign Keratosis (Mock)", "score": 0.03}
                ]
            }
        
    try:
        img_tensor = preprocess_image(image_bytes).to(device)
    except Exception as e:
        raise ValueError(f"Failed to process image: {e}")
        
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
    probs, indices = torch.topk(probabilities, 3)
    
    top_3 = []
    for prob, idx in zip(probs, indices):
        short_class = classes[idx.item()]
        human_class = HUMAN_READABLE_CLASSES.get(short_class, short_class)
        top_3.append({
            "class": human_class,
            "score": round(prob.item(), 4)
        })
        
    best_pred = top_3[0]
    
    return {
        "prediction": best_pred["class"],
        "confidence": best_pred["score"],
        "top_3": top_3
    }
