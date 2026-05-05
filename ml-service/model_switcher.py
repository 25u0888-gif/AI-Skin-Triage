"""
Model Switcher - Toggle between PyTorch and TensorFlow inference
Allows easy switching without modifying app.py
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "model_config.json"

DEFAULT_CONFIG = {
    "backend": "pytorch",  # Options: "pytorch" or "tensorflow"
    "pytorch_model": "model.pth",
    "tensorflow_model": "model_tensorflow.h5",
    "fallback_mode": True,
    "confidence_threshold": 0.6,
    "top_k": 3
}


def load_config():
    """Load model configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {CONFIG_FILE}")
            return config
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using defaults")
    
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save model configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error saving config: {e}")


def set_backend(backend_name):
    """
    Set the inference backend
    
    Args:
        backend_name: "pytorch" or "tensorflow"
    """
    if backend_name not in ["pytorch", "tensorflow"]:
        logger.error(f"Invalid backend: {backend_name}")
        return False
    
    config = load_config()
    config["backend"] = backend_name
    save_config(config)
    
    logger.info(f"✓ Backend set to: {backend_name}")
    return True


def get_predictor():
    """
    Get the appropriate prediction function based on config
    
    Returns:
        Prediction function (predict_image or predict_image_tensorflow)
    """
    config = load_config()
    backend = config.get("backend", "pytorch")
    
    logger.info(f"Loading {backend} backend...")
    
    try:
        if backend == "pytorch":
            from model import predict_image
            logger.info("✓ PyTorch backend loaded")
            return predict_image
        elif backend == "tensorflow":
            from model_tensorflow import predict_image_tensorflow
            logger.info("✓ TensorFlow backend loaded")
            return predict_image_tensorflow
        else:
            logger.error(f"Unknown backend: {backend}")
            return None
    except ImportError as e:
        logger.error(f"Failed to import {backend} module: {e}")
        logger.info("Falling back to PyTorch...")
        from model import predict_image
        return predict_image


def predict_with_config(image_path):
    """
    Predict using the configured backend
    
    Args:
        image_path: Path to the image
    
    Returns:
        Prediction result dictionary
    """
    config = load_config()
    predictor = get_predictor()
    
    if predictor is None:
        return {
            "error": "Failed to load prediction model",
            "warning": "System error occurred during model selection"
        }
    
    # Call with config parameters
    try:
        result = predictor(
            image_path=image_path,
            top_k=config.get("top_k", 3),
            confidence_threshold=config.get("confidence_threshold", 0.6)
        )
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            "error": f"Prediction failed: {str(e)}",
            "warning": "Failed to analyze image"
        }


def print_status():
    """Print current configuration status"""
    config = load_config()
    
    print(f"\n{'='*60}")
    print("Model Configuration Status")
    print(f"{'='*60}")
    print(f"Current Backend: {config['backend'].upper()}")
    print(f"PyTorch Model: {config['pytorch_model']}")
    print(f"  - Exists: {os.path.exists(config['pytorch_model'])}")
    print(f"  - Fallback: {config['fallback_mode']}")
    print(f"\nTensorFlow Model: {config['tensorflow_model']}")
    print(f"  - Exists: {os.path.exists(config['tensorflow_model'])}")
    print(f"\nSettings:")
    print(f"  - Confidence Threshold: {config['confidence_threshold']}")
    print(f"  - Top-K Predictions: {config['top_k']}")
    print(f"{'='*60}\n")


def initialize_config():
    """Create default config file if it doesn't exist"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        logger.info(f"Created default config at {CONFIG_FILE}")
    else:
        logger.info(f"Config already exists at {CONFIG_FILE}")


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    import sys
    
    initialize_config()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            print_status()
        
        elif command == "set-pytorch":
            set_backend("pytorch")
            print_status()
        
        elif command == "set-tensorflow":
            set_backend("tensorflow")
            print_status()
        
        elif command == "test":
            if len(sys.argv) > 2:
                image_path = sys.argv[2]
                result = predict_with_config(image_path)
                print("\nPrediction Result:")
                print(json.dumps(result, indent=2))
            else:
                print("Usage: python model_switcher.py test <image_path>")
        
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  status          - Show current configuration")
            print("  set-pytorch     - Switch to PyTorch backend")
            print("  set-tensorflow  - Switch to TensorFlow backend")
            print("  test <image>    - Test prediction on an image")
    else:
        print_status()
