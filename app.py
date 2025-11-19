import streamlit as st
import os
import pandas as pd
from googleapiclient.discovery import build
from google import generativeai as genai
from PIL import Image
import json
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure APIs
GENAI_API_KEY = os.getenv('GENAI_API_KEY')
VISION_API_KEY = os.getenv('VISION_API_KEY')

if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
else:
    st.error("Please set GENAI_API_KEY in .env file")

if not VISION_API_KEY:
    st.error("Please set VISION_API_KEY in .env file")

def extract_text_from_image(image_path):
    """Extract text using Google Vision API with API key"""

    # Read image and encode to base64
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode('utf-8')

    service = build('vision', 'v1', developerKey=VISION_API_KEY)

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

    response = request.execute()

    if 'responses' in response:
        if 'error' in response['responses'][0]:
            raise Exception(response['responses'][0]['error']['message'])

        texts = response['responses'][0].get('textAnnotations', [])
        return texts[0]['description'] if texts else ""

    return ""

def classify_equipment_type(image_path):
    """Classify equipment type using Gemini Vision (before OCR)"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Convert image to base64
        with open(image_path, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        prompt = """
        Classify this industrial equipment image into exactly ONE of these categories:
        - UPS / Inverter
        - Transformer
        - Stabilizer
        - Industrial PCB
        - Meter / Gauge
        - Breaker Panel
        - Battery Packs
        - Other Industrial Equipment

        Look at the shape, components, and visible features. Return only the category name, nothing else.
        """

        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_content}
        ])

        equipment_type = response.text.strip().split('\n')[0]
        return equipment_type if equipment_type else "Other Industrial Equipment"

    except Exception as e:
        st.warning(f"Equipment classification failed: {str(e)}")
        return "Other Industrial Equipment"

def detect_damage_and_faults(image_path, equipment_type):
    """Detect physical damage and faults using Gemini Vision"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        with open(image_path, "rb") as f:
            image_content = base64.b64encode(f.read()).decode('utf-8')

        prompt = f"""
        Analyze this {equipment_type} equipment image for physical damage and faults.

        Look for these specific damage types:
        - Burn marks / scorch marks
        - Loose or disconnected wires
        - Rust or corrosion
        - Broken display / LCD
        - Overheating signs (melted components, discoloration)
        - Water damage (wetness, corrosion patterns)
        - Mechanical damage (cracks, dents, breaks)
        - Missing components or parts

        Return a JSON array of detected damage types. If no damage found, return empty array [].
        Format: ["damage_type1", "damage_type2", ...]
        """

        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_content}
        ])

        try:
            damage_text = response.text.strip()
            # Extract JSON array
            if '[' in damage_text and ']' in damage_text:
                start = damage_text.find('[')
                end = damage_text.find(']', start) + 1
                json_str = damage_text[start:end]
                damages = json.loads(json_str)
                return damages if isinstance(damages, list) else []
            return []
        except:
            return []

    except Exception as e:
        st.warning(f"Damage detection failed: {str(e)}")
        return []

def parse_equipment_data(ocr_text, equipment_type, detected_damages):
    """Parse OCR text into structured data using Gemini"""
    try:
        model_name = 'gemini-2.5-flash'
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Gemini model configuration error: {e}")
        # Fallback to basic parsing
        return basic_parse_equipment(ocr_text)

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
        "detected_damages": {json.dumps(detected_damages)},
        "extracted_text": "{ocr_text}",
        "confidence": "high/medium/low"
    }}

    Consider the detected damages when assessing condition and operational status.
    """

    response = model.generate_content(prompt)

    try:
        # Extract JSON from response
        response_text = response.text.strip()
        # Find JSON block
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]

        parsed_data = json.loads(json_str)
        # Ensure detected_damages is included
        parsed_data['detected_damages'] = detected_damages
        return parsed_data
    except Exception as e:
        st.error(f"Error parsing Gemini response: {e}")
        return {"error": "Failed to parse equipment data"}

def basic_parse_equipment(ocr_text):
    """Basic parsing fallback when Gemini is not available"""
    # Simple regex-based parsing
    import re

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

    # Basic pattern matching
    lines = ocr_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for common manufacturing logos or brands
        if re.search(r'\b(Siemens|ABB|GE|Rockwell|Honeywell|Schneider|Mitsubishi|Fuji)\b', line, re.IGNORECASE):
            equipment_data["manufacturer"] = re.findall(r'\b(Siemens|ABB|GE|Rockwell|Honeywell|Schneider|Mitsubishi|Fuji)\b', line, re.IGNORECASE)[0].title()

        # Model patterns
        if re.search(r'model.*\b([A-Z0-9\-]+)\b', line, re.IGNORECASE):
            match = re.search(r'model.*\b([A-Z0-9\-]+)\b', line, re.IGNORECASE)
            equipment_data["model_number"] = match.group(1)

        # Serial number patterns
        if re.search(r'serial.*\b([A-Z0-9\-]+)\b', line, re.IGNORECASE):
            match = re.search(r'serial.*\b([A-Z0-9\-]+)\b', line, re.IGNORECASE)
            equipment_data["serial_number"] = match.group(1)

        # Voltage specs
        if 'v' in line.lower() and any(char.isdigit() for char in line):
            equipment_data["specifications"]["voltage"] = line.strip()

    # Assess condition based on keywords
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

def calculate_health_score(equipment_data, detected_damages):
    """Calculate equipment health score based on various factors"""
    score = 100  # Start with perfect score

    # Deduct points for detected damages
    damage_penalties = {
        'burn marks': 25,
        'scorch marks': 20,
        'corrosion': 15,
        'rust': 15,
        'broken display': 20,
        'overheating': 30,
        'loose wires': 10,
        'water damage': 40,
        'mechanical damage': 20,
        'missing components': 25
    }

    for damage in detected_damages:
        for damage_type, penalty in damage_penalties.items():
            if damage_type.lower() in damage.lower():
                score -= penalty
                break

    # Adjust based on condition assessment
    condition = equipment_data.get('condition', '').lower()
    if 'poor' in condition:
        score -= 20
    elif 'fair' in condition:
        score -= 10

    # Operational status impact
    operational = equipment_data.get('operational_status', '').lower()
    if 'non-functional' in operational:
        score -= 30
    elif 'limited' in operational:
        score -= 15

    return max(0, score)

def main():
    st.title("🚀 Advanced Industrial Equipment Image Analyzer")

    st.sidebar.header("📤 Upload Equipment Image")

    uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='📸 Uploaded Equipment Image', use_column_width=True)

        # Save temp image
        temp_path = "temp_equipment.jpg"
        image.save(temp_path)

        if st.button("🔍 Analyze Equipment"):
            with st.spinner("🔄 Processing image with AI..."):
                try:
                    # Step 1: Equipment Classification
                    st.subheader("🎯 Step 1: Equipment Classification")
                    with st.spinner("🤖 Analyzing equipment type..."):
                        equipment_type = classify_equipment_type(temp_path)

                    if equipment_type:
                        st.success(f"✅ Classified as: **{equipment_type}**")
                    else:
                        equipment_type = "Other Industrial Equipment"

                    # Step 2: Damage Detection
                    st.subheader("🔍 Step 2: Damage & Fault Detection")
                    with st.spinner("👀 Scanning for physical damage..."):
                        detected_damages = detect_damage_and_faults(temp_path, equipment_type)

                    if detected_damages:
                        st.error(f"⚠️ **Damages Detected:** {', '.join(detected_damages)}")
                        st.warning("⚠️ **Damage Assessment:** Physical damage may affect equipment functionality")
                    else:
                        st.success("✅ **No visible damage detected**")

                    # Step 3: OCR
                    st.subheader("📝 Step 3: Text Extraction")
                    ocr_text = extract_text_from_image(temp_path)

                    if ocr_text:
                        st.success("✅ Text extracted successfully!")
                        with st.expander("📋 Extracted Text"):
                            st.code(ocr_text, language="text")
                    else:
                        st.warning("⚠️ No text detected in the image")

                    # Step 4: AI Analysis
                    st.subheader("🧠 Step 4: AI-Powered Analysis")
                    with st.spinner("🔬 Analyzing with Gemini AI..."):
                        equipment_data = parse_equipment_data(ocr_text, equipment_type, detected_damages)

                    if "error" not in equipment_data:
                        st.success("🎉 Analysis Complete!")

                        # Enhanced display
                        st.header("📊 Analysis Results")

                        # Health score calculation
                        health_score = calculate_health_score(equipment_data, detected_damages)

                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🏥 Health Score", f"{health_score}%")
                        with col2:
                            st.metric("🔧 Equipment Type", equipment_type)
                        with col3:
                            confidence = equipment_data.get('confidence', 'medium').title()
                            st.metric("🎯 Confidence", confidence)

                        # Detailed results
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📋 Equipment Details")
                            st.write(f"**🏭 Manufacturer:** {equipment_data.get('manufacturer', 'Unknown')}")
                            st.write(f"**📦 Model:** {equipment_data.get('model_number', 'Unknown')}")
                            st.write(f"**🔢 Serial:** {equipment_data.get('serial_number', 'Unknown')}")

                            st.subheader("🏥 Condition & Status")
                            condition = equipment_data.get('condition', 'Unknown')
                            operational = equipment_data.get('operational_status', 'Unknown')

                            if 'good' in condition.lower() or 'new' in condition.lower():
                                st.success(f"🟢 **Condition:** {condition}")
                            elif 'fair' in condition.lower():
                                st.warning(f"🟡 **Condition:** {condition}")
                            else:
                                st.error(f"🔴 **Condition:** {condition}")

                            st.write(f"**⚙️ Status:** {operational}")

                        with col2:
                            st.subheader("⚙️ Specifications")
                            specs = equipment_data.get('specifications', {})
                            if specs:
                                for key, value in specs.items():
                                    if value:
                                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                            else:
                                st.write("*No specifications extracted*")

                            # Damage summary
                            if detected_damages:
                                st.subheader("🔧 Detected Damage/Faults")
                                for damage in detected_damages:
                                    st.error(f"• {damage}")
                            else:
                                st.success("✅ No damage detected")

                        # Export options
                        st.subheader("💾 Export Options")

                        col1, col2 = st.columns(2)
                        with col1:
                            json_str = json.dumps(equipment_data, indent=2)
                            st.download_button(
                                label="📥 Download JSON Report",
                                data=json_str,
                                file_name=f"{equipment_type.replace('/', '_')}_analysis.json",
                                mime="application/json"
                            )

                        with col2:
                            # Health report
                            report = f"""# Equipment Analysis Report

**Equipment Type:** {equipment_type}
**Health Score:** {health_score}%
**Condition:** {equipment_data.get('condition', 'Unknown')}
**Operational Status:** {equipment_data.get('operational_status', 'Unknown')}

## Detected Damages
{chr(10).join([f"- {d}" for d in detected_damages]) if detected_damages else "- None detected"}

## Extracted Information
**Manufacturer:** {equipment_data.get('manufacturer', 'Unknown')}
**Model:** {equipment_data.get('model_number', 'Unknown')}
**Serial:** {equipment_data.get('serial_number', 'Unknown')}

## Recommendations
- {'Immediate repair/service required' if health_score < 50 else 'Schedule maintenance' if health_score < 80 else 'Equipment in good condition'}

**Generated on:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                            st.download_button(
                                label="📄 Download Health Report",
                                data=report,
                                file_name=f"{equipment_type.replace('/', '_')}_report.txt",
                                mime="text/plain"
                            )

                    else:
                        st.error(equipment_data["error"])

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

    else:
        st.info("👈 **Get started:** Upload an equipment image to begin AI-powered analysis!")

        # Feature overview
        st.header("🎯 Analysis Features")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🤖 AI Classification")
            st.write("Automatically identifies equipment type from image")

        with col2:
            st.subheader("🔍 Damage Detection")
            st.write("Scans for physical damage, corrosion, loose wires")

        with col3:
            st.subheader("📊 Health Scoring")
            st.write("Provides comprehensive condition assessment")

if __name__ == "__main__":
    main()
