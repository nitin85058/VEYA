"""
AI Classifier module for Industrial Equipment Analyzer
Handles equipment classification and damage detection using Gemini AI
"""

import base64
from google import generativeai as genai
from config import APIConfig, AIModels, EQUIPMENT_CATEGORIES, DAMAGE_TYPES

# Initialize Gemini (ensure API key is set)
if APIConfig.GENAI_API_KEY:
    genai.configure(api_key=APIConfig.GENAI_API_KEY)

def classify_equipment_type(image_path):
    """
    Classify equipment type using Gemini Vision

    Args:
        image_path (str): Path to equipment image

    Returns:
        str: Classified equipment category
    """
    try:
        # Try models in order of preference
        model_name = None
        for potential_model in AIModels.CLASSIFICATION_MODELS:
            try:
                model = genai.GenerativeModel(potential_model)
                model_name = potential_model
                break
            except Exception:
                continue

        if not model_name:
            raise Exception("No available Gemini models found")

        # Read and encode image
        with open(image_path, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        # Create prompt for classification
        categories_str = "\n- ".join([""] + EQUIPMENT_CATEGORIES)
        prompt = f"""
        Classify this industrial equipment image into exactly ONE of these categories:
        {categories_str}

        Look at the shape, components, and visible features. Return ONLY the category name, nothing else.
        """

        # Generate classification
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_content}
        ])

        # Clean up response
        equipment_type = response.text.strip().split('\n')[0]

        # Validate classification
        if equipment_type not in EQUIPMENT_CATEGORIES:
            equipment_type = "Other Industrial Equipment"

        return equipment_type

    except Exception as e:
        print(f"Equipment classification failed: {str(e)}")
        return "Other Industrial Equipment"

def detect_damage_and_faults(image_path, equipment_type):
    """
    Detect physical damage and faults using Gemini Vision

    Args:
        image_path (str): Path to equipment image
        equipment_type (str): Type of equipment for context

    Returns:
        list: List of detected damage types
    """
    try:
        # Try models in order of preference
        model_name = None
        for potential_model in AIModels.ANALYSIS_MODELS:
            try:
                model = genai.GenerativeModel(potential_model)
                model_name = potential_model
                break
            except Exception:
                continue

        if not model_name:
            raise Exception("No available Gemini models found")

        # Read and encode image
        with open(image_path, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        # Create detailed damage detection prompt
        damage_types_str = "\n- ".join([""] + DAMAGE_TYPES)
        prompt = f"""
        Analyze this {equipment_type} equipment image for physical damage and faults.

        Look for these specific damage types:
        {damage_types_str}

        Return a JSON array of detected damage types. If no damage found, return empty array [].
        Format: ["damage_type1", "damage_type2", ...]

        Be specific about what you see - look for visual evidence like discoloration, burns, corrosion, broken parts, loose connections, water damage, overheating signs, etc.
        """

        # Generate analysis
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_content}
        ])

        # Parse response to extract JSON array
        response_text = response.text.strip()

        # Find JSON array in response
        import json
        if '[' in response_text and ']' in response_text:
            start = response_text.find('[')
            end = response_text.find(']', start) + 1
            json_str = response_text[start:end]

            try:
                damages = json.loads(json_str)
                if isinstance(damages, list):
                    return damages
            except Exception:
                pass

        return []

    except Exception as e:
        print(f"Damage detection failed: {str(e)}")
        return []

def analyze_compliance(image_path, ocr_text, equipment_type):
    """
    Analyze compliance based on visible labels and certifications

    Args:
        image_path (str): Path to equipment image
        ocr_text (str): Extracted text from image
        equipment_type (str): Type of equipment

    Returns:
        dict: Compliance analysis results
    """
    compliance_checks = {
        'iso_certified': False,
        'ce_marked': False,
        'rohs_compliant': False,
        'bis_certified': False,
        'ul_listed': False,
        'certifications_found': [],
        'potential_issues': []
    }

    # Check OCR text for certifications
    ocr_upper = ocr_text.upper()

    if 'ISO' in ocr_upper:
        compliance_checks['iso_certified'] = True
        compliance_checks['certifications_found'].append('ISO')

    if 'CE' in ocr_upper:
        compliance_checks['ce_marked'] = True
        compliance_checks['certifications_found'].append('CE')

    if 'ROHS' in ocr_upper or 'ROHS' in ocr_upper:
        compliance_checks['rohs_compliant'] = True
        compliance_checks['certifications_found'].append('RoHS')

    if 'BIS' in ocr_upper:
        compliance_checks['bis_certified'] = True
        compliance_checks['certifications_found'].append('BIS')

    if 'UL' in ocr_upper:
        compliance_checks['ul_listed'] = True
        compliance_checks['certifications_found'].append('UL')

    return compliance_checks

def detect_equipment_age(image_path, ocr_text):
    """
    Attempt to estimate equipment age based on visual and text clues

    Args:
        image_path (str): Path to equipment image
        ocr_text (str): Extracted text

    Returns:
        dict: Age estimation and confidence
    """
    age_indicators = {
        'modern_design': ['LED', 'DISPLAY', 'DIGITAL', 'MICROCONTROLLER'],
        'mid_age': ['LCD', 'ANALOG', 'TRANSISTOR'],
        'older_design': ['VACUUM TUBE', 'MECHANICAL DIALS', 'OUTDATED LABELS']
    }

    # Check for keywords in OCR text
    age_hints = []
    ocr_upper = ocr_text.upper()

    for age, indicators in age_indicators.items():
        for indicator in indicators:
            if indicator in ocr_upper:
                age_hints.append(age)
                break

    # Estimate age based on found indicators
    if 'modern_design' in age_hints:
        return {
            'estimated_age': 'Modern (< 5 years)',
            'confidence': 'medium',
            'indicators': [item for item in age_indicators['modern_design'] if item in ocr_upper]
        }
    elif 'mid_age' in age_hints:
        return {
            'estimated_age': 'Intermediate (5-15 years)',
            'confidence': 'low',
            'indicators': [item for item in age_indicators['mid_age'] if item in ocr_upper]
        }
    elif 'older_design' in age_hints:
        return {
            'estimated_age': 'Old (> 15 years)',
            'confidence': 'medium',
            'indicators': [item for item in age_indicators['older_design'] if item in ocr_upper]
        }
    else:
        return {
            'estimated_age': 'Unknown',
            'confidence': 'none',
            'indicators': []
        }
