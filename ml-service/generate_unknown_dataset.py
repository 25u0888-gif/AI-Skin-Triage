"""
Generate Synthetic Non-Skin Dataset for "Unknown" Class
Creates synthetic images of:
- Random objects
- Indoor scenes
- Backgrounds
- Natural textures
- Non-skin patterns

This helps train the model to reject non-skin images.
"""

import os
import numpy as np
from PIL import Image, ImageDraw
import random

print(f"\n{'='*70}")
print("Non-Skin Image Dataset Generator")
print(f"{'='*70}\n")

# Configuration
DATA_DIR = "../backend/data"
TRAIN_DIR = os.path.join(DATA_DIR, "train", "unknown")
VAL_DIR = os.path.join(DATA_DIR, "val", "unknown")

TARGET_TRAIN = 1000  # Target 1000+ training images
TARGET_VAL = 280     # Target 280+ validation images
IMG_SIZE = (224, 224)

# Create directories
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)

print(f"Creating directories:")
print(f"  Train: {TRAIN_DIR}")
print(f"  Val:   {VAL_DIR}\n")

# ============================================================================
# Image Generation Functions
# ============================================================================

def generate_random_objects():
    """Generate images of random colored shapes/objects"""
    img = Image.new('RGB', IMG_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw random shapes
    for _ in range(random.randint(3, 8)):
        color = tuple(np.random.randint(0, 256, 3))
        shape_type = random.choice(['circle', 'rectangle', 'polygon'])
        
        x1, y1 = random.randint(0, 150), random.randint(0, 150)
        x2, y2 = x1 + random.randint(20, 100), y1 + random.randint(20, 100)
        
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=color)
        elif shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=color)
        elif shape_type == 'polygon':
            points = [(x1, y1), (x2, y1), ((x1+x2)//2, y2)]
            draw.polygon(points, fill=color, outline=color)
    
    return img

def generate_natural_texture():
    """Generate natural texture patterns"""
    # Create Perlin-like noise (simple clouds effect)
    arr = np.zeros((IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.uint8)
    
    texture_type = random.choice(['clouds', 'wood', 'fabric', 'stone'])
    
    if texture_type == 'clouds':
        # Cloud-like pattern
        for i in range(IMG_SIZE[0]):
            for j in range(IMG_SIZE[1]):
                val = int(128 + 127 * np.sin(i/10) * np.cos(j/10) + 
                         50 * np.sin(i/30) * np.cos(j/30))
                arr[i, j] = val
    
    elif texture_type == 'wood':
        # Wood grain pattern
        for i in range(IMG_SIZE[0]):
            for j in range(IMG_SIZE[1]):
                val = int(100 + 50 * np.sin(i/5)) % 256
                arr[i, j] = val
    
    elif texture_type == 'fabric':
        # Fabric weave pattern
        for i in range(IMG_SIZE[0]):
            for j in range(IMG_SIZE[1]):
                val = 150 if (i + j) % 20 < 10 else 100
                arr[i, j] = val
    
    elif texture_type == 'stone':
        # Stone/concrete pattern
        arr = np.random.randint(80, 180, (IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.uint8)
        for i in range(0, IMG_SIZE[0], 20):
            arr[i, :] += np.random.randint(-20, 20, (IMG_SIZE[1], 3), dtype=np.int16)
    
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def generate_background():
    """Generate simple background images"""
    bg_type = random.choice(['solid', 'gradient', 'checkerboard', 'noise'])
    arr = np.zeros((IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.uint8)
    
    if bg_type == 'solid':
        color = tuple(np.random.randint(50, 220, 3))
        arr[:, :] = color
    
    elif bg_type == 'gradient':
        for i in range(IMG_SIZE[0]):
            color = tuple((np.array([50, 100, 150]) * i / IMG_SIZE[0]).astype(int))
            arr[i, :] = color
    
    elif bg_type == 'checkerboard':
        for i in range(IMG_SIZE[0]):
            for j in range(IMG_SIZE[1]):
                if (i // 16 + j // 16) % 2 == 0:
                    arr[i, j] = 200
                else:
                    arr[i, j] = 100
    
    elif bg_type == 'noise':
        arr = np.random.randint(100, 180, (IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.uint8)
    
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def generate_indoor_scene():
    """Generate indoor scene patterns"""
    img = Image.new('RGB', IMG_SIZE, color=(200, 180, 150))
    draw = ImageDraw.Draw(img)
    
    # Wall
    draw.rectangle([0, 0, IMG_SIZE[0], IMG_SIZE[1]], fill=(200, 180, 150))
    
    # Window
    window_color = (150, 200, 255)
    draw.rectangle([30, 30, 100, 100], fill=window_color)
    draw.rectangle([110, 30, 180, 100], fill=window_color)
    
    # Door
    draw.rectangle([140, 120, 200, 220], fill=(120, 80, 40))
    draw.ellipse([160, 160, 170, 170], fill=(200, 200, 100))
    
    # Floor
    draw.rectangle([0, 200, IMG_SIZE[0], IMG_SIZE[1]], fill=(150, 120, 100))
    
    # Add some lines for perspective
    for i in range(0, IMG_SIZE[0], 20):
        draw.line([(i, 200), (i + 20, IMG_SIZE[1])], fill=(100, 80, 60), width=2)
    
    return img

def generate_text_pattern():
    """Generate text and pattern images"""
    img = Image.new('RGB', IMG_SIZE, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    pattern_type = random.choice(['lines', 'dots', 'grids', 'stripes'])
    
    if pattern_type == 'lines':
        for i in range(0, IMG_SIZE[0], random.randint(10, 30)):
            draw.line([(i, 0), (i, IMG_SIZE[1])], fill=(0, 0, 0), width=2)
    
    elif pattern_type == 'dots':
        for i in range(0, IMG_SIZE[0], 20):
            for j in range(0, IMG_SIZE[1], 20):
                draw.ellipse([i, j, i+10, j+10], fill=(0, 0, 0))
    
    elif pattern_type == 'grids':
        for i in range(0, IMG_SIZE[0], 20):
            draw.line([(i, 0), (i, IMG_SIZE[1])], fill=(0, 0, 0), width=1)
        for j in range(0, IMG_SIZE[1], 20):
            draw.line([(0, j), (IMG_SIZE[0], j)], fill=(0, 0, 0), width=1)
    
    elif pattern_type == 'stripes':
        for i in range(0, IMG_SIZE[0], 15):
            draw.rectangle([i, 0, i+10, IMG_SIZE[1]], fill=(0, 0, 0))
    
    return img

def generate_random_noise():
    """Generate random noise images"""
    arr = np.random.randint(0, 256, (IMG_SIZE[0], IMG_SIZE[1], 3), dtype=np.uint8)
    return Image.fromarray(arr)

# ============================================================================
# Generate Training Images
# ============================================================================

print(f"Generating {TARGET_TRAIN} training images...")

generators = [
    generate_random_objects,
    generate_natural_texture,
    generate_background,
    generate_indoor_scene,
    generate_text_pattern,
    generate_random_noise
]

for i in range(TARGET_TRAIN):
    # Rotate through generators
    generator = generators[i % len(generators)]
    img = generator()
    
    # Save image
    img_path = os.path.join(TRAIN_DIR, f"unknown_train_{i:05d}.jpg")
    img.save(img_path, quality=85)
    
    if (i + 1) % 100 == 0:
        print(f"  Generated {i + 1}/{TARGET_TRAIN} training images")

print(f"✓ Training images generated: {TARGET_TRAIN}")

# ============================================================================
# Generate Validation Images
# ============================================================================

print(f"\nGenerating {TARGET_VAL} validation images...")

for i in range(TARGET_VAL):
    generator = generators[i % len(generators)]
    img = generator()
    
    # Save image
    img_path = os.path.join(VAL_DIR, f"unknown_val_{i:05d}.jpg")
    img.save(img_path, quality=85)
    
    if (i + 1) % 50 == 0:
        print(f"  Generated {i + 1}/{TARGET_VAL} validation images")

print(f"✓ Validation images generated: {TARGET_VAL}")

# ============================================================================
# Summary
# ============================================================================

train_count = len(os.listdir(TRAIN_DIR))
val_count = len(os.listdir(VAL_DIR))

print(f"\n{'='*70}")
print("DATASET GENERATION COMPLETE")
print(f"{'='*70}\n")

print(f"Train directory: {TRAIN_DIR}")
print(f"  Images: {train_count}")

print(f"\nVal directory: {VAL_DIR}")
print(f"  Images: {val_count}")

print(f"\nTotal 'unknown' class images: {train_count + val_count}")

print(f"\nThese synthetic images include:")
print(f"  ✓ Random colored objects")
print(f"  ✓ Natural textures (clouds, wood, fabric, stone)")
print(f"  ✓ Background patterns")
print(f"  ✓ Indoor scene simulations")
print(f"  ✓ Text and geometric patterns")
print(f"  ✓ Random noise")

print(f"\nNext steps:")
print(f"  1. Review some generated images to ensure diversity")
print(f"  2. Train model with: python train_with_unknown.py")
print(f"  3. Validate with: python validate_with_safety.py")
print(f"  4. Deploy new model_tensorflow_with_unknown.h5\n")
