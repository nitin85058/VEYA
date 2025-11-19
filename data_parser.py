"""
Data Parser module for Industrial Equipment Analyzer
Handles OCR text analysis and structured data extraction using AI
"""

import re
from google import generativeai as genai
from config import APIConfig, AIModels


def parse_equipment_data(ocr_text, equipment_type, detected_damages):
    """
    Parse OCR text into structured equipment data using Gemini AI

    Args:
        ocr_text (str): Extracted text from OCR
        equipment_type (str): Classified equipment type
        detected_damages (list): List of detected damage types

    Returns:
        dict: Structured equipment data
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

        # Create comprehensive analysis prompt
        prompt = f"""
        Analyze this OCR text from an image of industrial electronic equipment and extract structured information.

        Equipment Type: {equipment_type}
        Detected Damages: {', '.join(detected_damages) if detected_damages else 'None detected'}

        OCR Text:
        {ocr_text}

        Provide a JSON response with the following structure:
        {{
            "equipment_type": "{equipment_type}",
            "manufacturer": "string",
            "model_number": "string",
            "serial_number": "string",
            "specifications": {{
                "voltage": "string",
                "current": "string",
                "frequency": "string",
                "temperature_range": "string",
                "power_rating": "string"
            }},
            "condition": "string (good/fair/poor based on damages and text)",
            "operational_status": "string (functional/limited/non-functional based on damages)",
            "detected_damages": {list(detected_damages)},
            "extracted_text": "{ocr_text}",
            "confidence": "high/medium/low"
        }}

        Consider the detected damages when assessing condition and operational status.
        Fill in as many fields as possible from the text. Leave fields empty if information is not available.
        """

        # Generate analysis
        response = model.generate_content(prompt)

        # Parse JSON response
        response_text = response.text.strip()

        # Extract JSON block
        import json
        if '{' in response_text and '}' in response_text:
            # Find the main JSON object
            start = response_text.find('{')
            # Count braces to find matching closing brace
            brace_count = 0
            end = start
            for i, char in enumerate(response_text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break

            json_str = response_text[start:end]

            try:
                parsed_data = json.loads(json_str)
                # Ensure detected_damages is included
                parsed_data['detected_damages'] = detected_damages
                return parsed_data
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                # Fallback to basic parsing
                return basic_parse_equipment(ocr_text)

        # If no JSON found, use basic parsing
        return basic_parse_equipment(ocr_text)

    except Exception as e:
        print(f"AI parsing failed: {str(e)}")
        return basic_parse_equipment(ocr_text)


def basic_parse_equipment(ocr_text):
    """
    Fallback parsing using regex patterns when AI is unavailable

    Args:
        ocr_text (str): OCR extracted text

    Returns:
        dict: Basic equipment data
    """
    equipment_data = {
        "equipment_type": "Unknown",
        "manufacturer": "",
        "model_number": "",
        "serial_number": "",
        "specifications": {},
        "condition": "Unknown - Unable to assess without AI",
        "operational_status": "Unknown - Unable to assess without AI",
        "detected_damages": [],
        "extracted_text": ocr_text,
        "confidence": "low"
    }

    # Split text into lines for processing
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

    for line in lines:
        line = line.upper()  # Case insensitive matching

        # Manufacturer detection using common industrial brands
        manufacturers = ['SIEMENS', 'ABB', 'GE', 'ROCKWELL', 'HONEYWELL', 'SCHNEIDER', 'MITSUBISHI', 'FUJI', 'DELTA', 'TOSHIBA']
        for manufacturer in manufacturers:
            if manufacturer in line and not equipment_data["manufacturer"]:
                equipment_data["manufacturer"] = manufacturer.title()
                break

        # Model number patterns
        model_patterns = [
            r'MODEL\s*[#:]*\s*([A-Z0-9\-]+)',  # MODEL: XYZ-123
            r'#([A-Z0-9\-]+)',  # #M123
            r'MDL\s*([A-Z0-9\-]+)',  # MDL ABC123
        ]

        for pattern in model_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and not equipment_data["model_number"]:
                equipment_data["model_number"] = match.group(1)
                break

        # Serial number patterns
        serial_patterns = [
            r'SERIAL\s*[#:]*\s*([A-Z0-9\-]+)',  # SERIAL: ABC123
            r'SN[#:]*\s*([A-Z0-9\-]+)',  # SN: 123456
            r'S/N[#:]*\s*([A-Z0-9\-]+)',  # S/N: XYZ789
        ]

        for pattern in serial_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and not equipment_data["serial_number"]:
                equipment_data["serial_number"] = match.group(1)
                break

        # Voltage specifications
        voltage_patterns = [
            r'(\d+(?:\.\d+)?)\s*V(?:OLTS?)?',  # 220V, 24 VOLTS
            r'(\d+(?:\.\d+)?)\s*VAC',  # 220 VAC
            r'(\d+(?:\.\d+)?)\s*VDC',  # 24 VDC
        ]

        for pattern in voltage_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and 'voltage' not in equipment_data["specifications"]:
                equipment_data["specifications"]["voltage"] = match.group(1) + 'V'
                break

    # Assessment based on keywords (will be enhanced with detected_damages in main app)
    ocr_lower = ocr_text.lower()
    if any(word in ocr_lower for word in ['new', 'unused', 'never used', 'factory', 'boxed']):
        equipment_data['condition'] = 'Good - Appears new/unused'
        equipment_data['operational_status'] = 'Fully functional - New equipment'
        equipment_data['confidence'] = 'medium'
    elif any(word in ocr_lower for word in ['used', 'service', 'maintenance required']):
        equipment_data['condition'] = 'Fair - Shows signs of use'
        equipment_data['operational_status'] = 'Limited functionality - May need maintenance'
        equipment_data['confidence'] = 'medium'
    elif any(word in ocr_lower for word in ['rust', 'corrosion', 'damaged', 'broken', 'faulty']):
        equipment_data['condition'] = 'Poor - Visible damage/wear'
        equipment_data['operational_status'] = 'Non-functional - Requires repair'
        equipment_data['confidence'] = 'medium'
    elif 'voltage' in ocr_lower or 'current' in ocr_lower or 'power' in ocr_lower:
        equipment_data['condition'] = 'Good - Specifications readable'
        equipment_data['operational_status'] = 'Functional - Based on available specs'
        equipment_data['confidence'] = 'medium'

    return equipment_data


def extract_additional_specs(ocr_text):
    """
    Extract additional technical specifications from OCR text

    Args:
        ocr_text (str): Full OCR text

    Returns:
        dict: Additional specifications found
    """
    specs = {}

    # Current/Power specifications
    current_match = re.search(r'(\d+(?:\.\d+)?)\s*A(?:MPS?)?', ocr_text, re.IGNORECASE)
    if current_match:
        specs['current'] = current_match.group(1) + 'A'

    # Frequency specifications
    freq_match = re.search(r'(\d+(?:\.\d+)?)\s*H(?:Z)?', ocr_text, re.IGNORECASE)
    if freq_match:
        specs['frequency'] = freq_match.group(1) + 'Hz'

    # Temperature range
    temp_match = re.search(r'(-?\d+)\s*(?:to|[-~])\s*(-?\d+)\s*[°]?C', ocr_text, re.IGNORECASE)
    if temp_match:
        specs['temperature_range'] = f"{temp_match.group(1)}°C to {temp_match.group(2)}°C"

    # Power rating
    power_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:W|KW|MW)(?:ATTS?)?', ocr_text, re.IGNORECASE)
    if power_match:
        value = power_match.group(1)
        unit = power_match.group(2).upper()
        specs['power_rating'] = f"{value}{unit}"

    return specs


def generate_recommendations(equipment_data, health_score, detected_damages):
    """
    Generate service and maintenance recommendations

    Args:
        equipment_data (dict): Equipment analysis data
        health_score (int): Health score 0-100
        detected_damages (list): List of detected damages

    Returns:
        dict: Recommendations and insights
    """
    recommendations = {
        'service_actions': [],
        'spare_parts': [],
        'risk_assessment': 'Low',
        'maintenance_schedule': '',
        'cost_estimate': 'N/A'
    }

    # Service recommendations based on damage
    if 'burn marks' in detected_damages or 'overheating' in detected_damages:
        recommendations['service_actions'].append('Immediate electrical inspection required')
        recommendations['service_actions'].append('Replace damaged components')
        recommendations['risk_assessment'] = 'High'

    # Health-based recommendations
    if health_score < 30:
        recommendations['maintenance_schedule'] = 'Immediate attention required'
        recommendations['service_actions'].append('Complete system overhaul')
        recommendations['risk_assessment'] = 'Critical'

    elif health_score < 60:
        recommendations['maintenance_schedule'] = 'Schedule within 1 week'
        recommendations['service_actions'].append('Repair identified damages')
        recommendations['risk_assessment'] = 'High'

    elif health_score < 80:
        recommendations['maintenance_schedule'] = 'Schedule within 1 month'
        recommendations['service_actions'].append('Routine inspection and cleaning')
        recommendations['risk_assessment'] = 'Medium'

    else:
        recommendations['maintenance_schedule'] = 'Schedule within 6 months'
        recommendations['service_actions'].append('Routine preventive maintenance')
        recommendations['risk_assessment'] = 'Low'

    return recommendations
