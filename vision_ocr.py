"""
Vision OCR module for Industrial Equipment Analyzer
Handles Google Cloud Vision API for text extraction and image processing
"""

import base64
from googleapiclient.discovery import build
from config import APIConfig

def extract_text_from_image(image_path):
    """
    Extract text from image using Google Cloud Vision API

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Extracted text from the image
    """
    try:
        # Read and encode image to base64
        with open(image_path, "rb") as image_file:
            image_content = base64.b64encode(image_file.read()).decode('utf-8')

        # Build Vision API service
        service = build('vision', 'v1', developerKey=APIConfig.VISION_API_KEY)

        # Prepare request
        request = service.images().annotate(body={
            'requests': [{
                'image': {
                    'content': image_content
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }]
        })

        # Execute request
        response = request.execute()

        # Extract text from response
        if 'responses' in response:
            if 'error' in response['responses'][0]:
                raise Exception(response['responses'][0]['error']['message'])

            texts = response['responses'][0].get('textAnnotations', [])
            return texts[0]['description'] if texts else ""

        return ""

    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")

def detect_image_features(image_path, feature_types=None):
    """
    Detect multiple features from an image

    Args:
        image_path (str): Path to image file
        feature_types (list): List of feature types to detect (LABEL_DETECTION, OBJECT_LOCALIZATION, etc.)

    Returns:
        dict: Vision API response with features
    """
    try:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        service = build('vision', 'v1', developerKey=APIConfig.VISION_API_KEY)

        # Default features if none specified
        if feature_types is None:
            feature_types = ['LABEL_DETECTION', 'OBJECT_LOCALIZATION', 'TEXT_DETECTION']

        features = [{'type': ft} for ft in feature_types]

        request = service.images().annotate(body={
            'requests': [{
                'image': {'content': image_content},
                'features': features
            }]
        })

        response = request.execute()
        return response

    except Exception as e:
        raise Exception(f"Image feature detection failed: {str(e)}")

def get_image_metadata(image_path):
    """
    Extract basic image metadata and characteristics

    Args:
        image_path (str): Path to image file

    Returns:
        dict: Basic image information
    """
    from PIL import Image
    import os

    try:
        # Open image with PIL
        img = Image.open(image_path)
        metadata = {
            'size': img.size,
            'format': img.format,
            'mode': img.mode,
            'width': img.width,
            'height': img.height,
            'file_size': os.path.getsize(image_path),
            'has_alpha': img.mode in ('RGBA', 'LA', 'PA')
        }
        img.close()
        return metadata

    except Exception as e:
        raise Exception(f"Image metadata extraction failed: {str(e)}")

def validate_image_format(image_path):
    """
    Validate if the image file is supported and readable

    Args:
        image_path (str): Path to check

    Returns:
        bool: True if valid image format
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        img.verify()  # Check if image is corrupted
        img.close()
        return True
    except Exception:
        return False
