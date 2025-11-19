"""
Configuration file for Industrial Equipment Analyzer
Contains API keys, constants, and system settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Configuration
class APIConfig:
    GENAI_API_KEY = os.getenv('GENAI_API_KEY', '')
    VISION_API_KEY = os.getenv('VISION_API_KEY', '')

    @classmethod
    def validate_credentials(cls):
        """Validate that required API keys are available"""
        issues = []
        if not cls.GENAI_API_KEY:
            issues.append("GENAI_API_KEY not found in .env file")
        if not cls.VISION_API_KEY:
            issues.append("VISION_API_KEY not found in .env file")
        return issues

# AI Model Configuration
class AIModels:
    # Using only gemini-2.5-flash as requested (Note: this model does not exist in current Google Gemini API)
    CLASSIFICATION_MODELS = ['gemini-2.5-flash']
    ANALYSIS_MODELS = ['gemini-2.5-flash']

# Equipment Categories
EQUIPMENT_CATEGORIES = [
    'UPS / Inverter', 'Transformer', 'Stabilizer', 'Industrial PCB',
    'Meter / Gauge', 'Breaker Panel', 'Battery Packs', 'Other Industrial Equipment'
]

# Damage Types to Detect
DAMAGE_TYPES = [
    'burn marks', 'scorch marks', 'corrosion', 'rust',
    'broken display', 'overheating', 'loose wires',
    'water damage', 'mechanical damage', 'missing components'
]

# Health Scoring Penalties
HEALTH_PENALTIES = {
    'burn marks': 25, 'scorch marks': 20, 'corrosion': 15, 'rust': 15,
    'broken display': 20, 'overheating': 30, 'loose wires': 10,
    'water damage': 40, 'mechanical damage': 20, 'missing components': 25
}

# File Paths and Settings
class SystemSettings:
    TEMP_IMAGE_FILE = 'temp_equipment.jpg'
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

    # UI Settings
    TITLE = "🚀 Advanced Industrial Equipment Image Analyzer"
    FEATURE_OVERVIEW = [
        ("🤖 AI Classification", "Automatically identifies equipment type from image"),
        ("🔍 Damage Detection", "Scans for physical damage, corrosion, loose wires"),
        ("📊 Health Scoring", "Provides comprehensive condition assessment")
    ]
