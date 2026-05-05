"""
HAM10000 Dataset Preparation Utility
Splits HAM10000 images into train/val directories by disease class
"""

import os
import shutil
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disease class directories that will be created
DISEASE_CLASSES = ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']

class HAM10000DatasetSplitter:
    def __init__(self, source_images_dirs, metadata_path, output_dir, train_split=0.8):
        """
        Initialize dataset splitter
        
        Args:
            source_images_dirs: List of directories containing HAM10000 images
            metadata_path: Path to HAM10000_metadata.csv
            output_dir: Where to save train/val split
            train_split: Fraction of data for training (default 0.8)
        """
        self.source_dirs = source_images_dirs
        self.metadata_path = metadata_path
        self.output_dir = output_dir
        self.train_split = train_split
        self.metadata = None
        
    def load_metadata(self):
        """Load and validate metadata CSV"""
        logger.info(f"Loading metadata from: {self.metadata_path}")
        
        if not os.path.exists(self.metadata_path):
            logger.error(f"Metadata file not found: {self.metadata_path}")
            raise FileNotFoundError(self.metadata_path)
        
        self.metadata = pd.read_csv(self.metadata_path)
        logger.info(f"✓ Loaded {len(self.metadata)} records")
        logger.info(f"✓ Columns: {list(self.metadata.columns)}")
        logger.info(f"✓ Diseases: {self.metadata['dx'].unique()}")
        
        return self.metadata
    
    def verify_images(self):
        """Check that all image files exist"""
        logger.info("\nVerifying image files...")
        
        missing_count = 0
        found_count = 0
        
        for idx, row in self.metadata.iterrows():
            image_id = row['image_id']
            found = False
            
            for source_dir in self.source_dirs:
                image_path = os.path.join(source_dir, f"{image_id}.jpg")
                if os.path.exists(image_path):
                    found = True
                    found_count += 1
                    break
            
            if not found:
                missing_count += 1
                logger.warning(f"  Missing: {image_id}.jpg")
        
        logger.info(f"✓ Found: {found_count}/{len(self.metadata)}")
        if missing_count > 0:
            logger.warning(f"⚠️  Missing: {missing_count} images")
        
        return found_count == len(self.metadata)
    
    def create_directory_structure(self):
        """Create train/val directories for each disease class"""
        logger.info("\nCreating directory structure...")
        
        for split in ['train', 'val']:
            for disease in DISEASE_CLASSES:
                dir_path = os.path.join(self.output_dir, split, disease)
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"✓ Created: {dir_path}")
    
    def find_image_path(self, image_id):
        """Find image file in source directories"""
        for source_dir in self.source_dirs:
            image_path = os.path.join(source_dir, f"{image_id}.jpg")
            if os.path.exists(image_path):
                return image_path
        return None
    
    def split_dataset(self):
        """Split dataset into train/val by disease class"""
        logger.info("\nSplitting dataset by disease class...")
        
        self.create_directory_structure()
        
        total_copied = 0
        total_failed = 0
        
        for disease in DISEASE_CLASSES:
            logger.info(f"\nProcessing {disease}...")
            
            # Get all images for this disease
            disease_images = self.metadata[self.metadata['dx'] == disease]['image_id'].tolist()
            logger.info(f"  Total images: {len(disease_images)}")
            
            # Split into train/val
            train_images, val_images = train_test_split(
                disease_images,
                train_size=self.train_split,
                random_state=42
            )
            
            logger.info(f"  Train: {len(train_images)} | Val: {len(val_images)}")
            
            # Copy training images
            for image_id in train_images:
                src = self.find_image_path(image_id)
                if src:
                    dst = os.path.join(self.output_dir, 'train', disease, f"{image_id}.jpg")
                    try:
                        shutil.copy2(src, dst)
                        total_copied += 1
                    except Exception as e:
                        logger.error(f"  Error copying {image_id}: {e}")
                        total_failed += 1
                else:
                    logger.warning(f"  Not found: {image_id}")
                    total_failed += 1
            
            # Copy validation images
            for image_id in val_images:
                src = self.find_image_path(image_id)
                if src:
                    dst = os.path.join(self.output_dir, 'val', disease, f"{image_id}.jpg")
                    try:
                        shutil.copy2(src, dst)
                        total_copied += 1
                    except Exception as e:
                        logger.error(f"  Error copying {image_id}: {e}")
                        total_failed += 1
                else:
                    logger.warning(f"  Not found: {image_id}")
                    total_failed += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DATASET SPLIT COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total copied: {total_copied}")
        logger.info(f"Total failed: {total_failed}")
        logger.info(f"Output directory: {self.output_dir}")
        
        return total_copied, total_failed
    
    def verify_split(self):
        """Verify the split dataset"""
        logger.info("\nVerifying split dataset...")
        
        train_count = 0
        val_count = 0
        
        for disease in DISEASE_CLASSES:
            train_dir = os.path.join(self.output_dir, 'train', disease)
            val_dir = os.path.join(self.output_dir, 'val', disease)
            
            train_images = len(os.listdir(train_dir))
            val_images = len(os.listdir(val_dir))
            
            train_count += train_images
            val_count += val_images
            
            logger.info(f"{disease:8} - Train: {train_images:4} | Val: {val_images:4}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL: Train: {train_count} | Val: {val_count}")
        logger.info(f"Ratio: {train_count/(train_count+val_count)*100:.1f}% train / {val_count/(train_count+val_count)*100:.1f}% val")
        logger.info(f"{'='*60}\n")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Split HAM10000 dataset for training')
    parser.add_argument('--metadata', default='../backend/data/HAM10000_metadata.csv',
                       help='Path to HAM10000_metadata.csv')
    parser.add_argument('--images', nargs='+',
                       default=['../backend/data/HAM10000_images_part_1',
                               '../backend/data/HAM10000_images_part_2'],
                       help='Paths to HAM10000 image directories')
    parser.add_argument('--output', default='../backend/data',
                       help='Output directory for train/val split')
    parser.add_argument('--train-split', type=float, default=0.8,
                       help='Fraction of data for training (default: 0.8)')
    
    args = parser.parse_args()
    
    logger.info(f"\n{'='*60}")
    logger.info("HAM10000 Dataset Preparation")
    logger.info(f"{'='*60}")
    logger.info(f"Metadata: {args.metadata}")
    logger.info(f"Images: {args.images}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Train/Val Split: {args.train_split:.1%} / {1-args.train_split:.1%}")
    logger.info(f"{'='*60}\n")
    
    try:
        splitter = HAM10000DatasetSplitter(
            source_images_dirs=args.images,
            metadata_path=args.metadata,
            output_dir=args.output,
            train_split=args.train_split
        )
        
        # Load and verify metadata
        splitter.load_metadata()
        
        # Verify images exist
        if not splitter.verify_images():
            logger.warning("⚠️  Some images are missing, but continuing...")
        
        # Split dataset
        total_copied, total_failed = splitter.split_dataset()
        
        # Verify the split
        splitter.verify_split()
        
        logger.info("✓ Dataset preparation complete!")
        logger.info(f"Ready to train with: {args.output}/train and {args.output}/val")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
