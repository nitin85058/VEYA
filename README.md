# 🚀 Advanced Industrial Equipment Image Analyzer

A sophisticated, modular AI-powered system for analyzing industrial equipment from images. Features automatic equipment classification, damage detection, interactive health scoring, and comprehensive reporting with advanced analytics dashboards.

## 🏗️ **Modular Architecture (Phase 2 Complete)**

**Project Structure (Feature-Based Organization):**
```
industrial-equipment-analyzer/
├── main.py              # 🎯 Main application coordinator
├── config.py            # ⚙️ API configs, constants, settings
├── vision_ocr.py        # 🖼️ OCR processing & Vision API utilities
├── ai_classifier.py     # 🧠 Equipment classification & damage detection
├── data_parser.py       # 📊 Text analysis & structured data extraction
├── health_analyzer.py   # 📈 Health scoring & analytics
├── ui_components.py     # 🎨 Streamlit UI with interactive dashboards
├── requirements.txt     # 📦 Dependencies
├── .env.example         # 🔑 API key templates
└── README.md           # 📖 This documentation
```

## 🎯 **Core Features (Phase 1 Complete)**

### 🤖 **AI-Powered Equipment Classification**
- Automatically identifies 8+ equipment types (UPS, Transformers, Breakers, etc.)
- Uses Gemini Vision for visual pattern recognition
- Context-aware classification for industrial settings

### 🔍 **Advanced Damage Detection**
- Scans for 10+ types of physical damage (burn marks, rust, corrosion, etc.)
- Visual fault detection using AI image analysis
- Equipment-specific damage patterns recognition

### 📊 **Comprehensive Health Scoring**
- Calculates health percentage (0-100%) based on multiple factors
- Considers detected damages, condition assessment, and operational status
- Penalizes for different damage types with configurable weights

### 📝 **OCR & Text Analysis**
- Google Cloud Vision API for high-accuracy text extraction
- Automated parsing of manufacturer, model, and serial numbers
- Technical specification extraction from equipment labels

## 📊 **Advanced Analytics Dashboard (Phase 2 Complete)**

### 🎨 **Interactive Health Visualization**
- Health score gauge with real-time color coding
- Damage impact charts showing health penalties
- Trend analysis with simulated performance curves
- Comparative analysis across equipment types

### 📈 **Smart Analytics Dashboard**
- **Health Metrics Tab**: Interactive gauges and scoring breakdown
- **Damage Analysis Tab**: Impact charts and severity classification
- **Health Trends Tab**: Performance evolution and insights
- **Comparative View Tab**: Fleet-wide equipment analysis
- **Maintenance Dashboard Tab**: Risk assessment and recommendations

### 🏗️ **Professional Reporting System**
- Enhanced JSON export with detailed analysis metadata
- Human-readable health reports with actionable recommendations
- Multi-format export compatibility
- Automated report generation with timestamp and version tracking

## 🚀 **Getting Started**

### Quick Start
```bash
# 1. Clone/project setup
git clone <repository-url>
cd industrial-equipment-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env with your actual API keys

# 4. Run the application
streamlit run main.py
```

### 🔧 **Current Configuration Notes**
- **AI Model**: Currently set to `gemini-2.5-flash` (configured as requested)
- **Architecture**: Modular 7-file design with feature separation
- **Application Status**: Fully functional Streamlit dashboard

### 🔑 **API Configuration Required**

#### Gemini AI API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create new API key
3. Copy to `.env` as `GENAI_API_KEY`
4. **Note**: Current system uses `gemini-2.5-flash` (requested model)

#### Google Cloud Vision API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Vision API & create API key
3. Copy to `.env` as `VISION_API_KEY`

### 🖥️ **Usage**

1. **Upload Image**: Upload equipment photo via sidebar
2. **Click Analyze**: Watch 5-step AI analysis process
3. **Review Results**: Equipment details, damages, health score
4. **Export Reports**: Download JSON data & health reports
5. **Advanced Analysis**: Optional compliance & age estimation

## 🔧 **Technical Details**

### **Analysis Pipeline**
```
📤 Image Upload → 🎯 Classification → 🔍 Damage Detection
             ↓
📝 OCR Processing → 🧠 AI Analysis → 📊 Health Scoring
             ↓
📈 Risk Assessment → 💾 Report Generation
```

### **AI Model Configuration**
- **Current**: `gemini-2.5-flash` (configured as requested)
- **Fallback**: Basic regex parsing when AI unavailable
- **Note**: System includes multi-model support with graceful degradation

### **Key Technologies**
- **Frontend**: Streamlit (reactive web UI)
- **OCR Engine**: Google Cloud Vision API
- **AI Analysis**: Google Gemini 2.5 Flash + fallback processing
- **Image Processing**: Pillow
- **Environment**: dotenv configuration
- **Data Export**: JSON + health reports
- **Architecture**: 7 modular feature-based components

### **Supported Equipment Types (8 Categories)**
- UPS / Inverter
- Transformer
- Stabilizer
- Industrial PCB
- Meter / Gauge
- Breaker Panel
- Battery Packs
- Other Industrial Equipment

### **Damages Detected (10+ Types)**
- Burn marks & scorch marks
- Loose or disconnected wires
- Rust & corrosion
- Broken display / LCD
- Overheating signs
- Water damage
- Mechanical damage
- Missing components

## 🤖 **Technical Implementation**

### **Phase 1: Core AI Features**
- **Gemini Vision AI**: Advanced image recognition and classification
- **Google Cloud Vision**: High-accuracy OCR and text extraction
- **Multi-format Reporting**: JSON and human-readable reports
- **Real-time Processing**: Live analysis with progress tracking

### **Phase 2: Interactive Analytics**
- **Plotly Visualizations**: Interactive charts and health gauges
- **Comparative Analysis**: Side-by-side equipment performance
- **Trend Forecasting**: Simulated health evolution patterns
- **Damage Impact Modeling**: Quantified health score reductions
- **Maintenance Intelligence**: Automated risk assessment and scheduling

### **🔍 Damage Recognition System**
- **10+ Damage Types**: Comprehensive industrial fault detection
- **Severity Classification**: Color-coded impact levels (High/Medium/Low)
- **Impact Quantification**: Numerical health score penalties
- **Pattern Recognition**: AI-powered specific damage identification

## 🎨 **UI/UX Highlights**

- **Progressive Analysis**: Clear 5-step workflow with status updates
- **Visual Status Indicators**: Color-coded health and condition displays
- **Interactive Components**: Expandable sections, multiple export formats
- **Professional Dashboard**: Industry-standard visualization
- **Responsive Design**: Works on desktop and mobile browsers

## 🚀 **Performance & Scalability**

- **Modular Architecture**: Easy to extend and maintain
- **API-Based Design**: Cloud AI services for reliability
- **Fallback Systems**: Works with partial API availability
- **Export Capabilities**: Multiple output formats for integration
- **Configuration Management**: Environment-based settings

## 🛠️ **Development & Customization**

Each module can be independently developed, tested, and extended:

- **`vision_ocr.py`** - Add new OCR engines or image formats
- **`ai_classifier.py`** - Extend equipment types or damage categories
- **`health_analyzer.py`** - Customize scoring algorithms
- **`ui_components.py`** - Enhance dashboard features
- **`config.py`** - Add new API integrations or settings

---

**Built with ❤️ for Industrial Equipment Inspection & Maintenance**

## Usage

1. Upload an image of industrial equipment using the sidebar
2. Click "Analyze Equipment" to process
3. View OCR results and AI analysis
4. See condition and operational status
5. Download the JSON report

## Output Structure

The application generates JSON with:
- Equipment type, manufacturer, model, serial
- Technical specifications (voltage, power, etc.)
- Condition assessment (good/fair/poor)
- Operational status (functional/limited/non-functional)
- Raw extracted text
- Confidence level

## Troubleshooting

- **API Errors**: Verify your API keys and credentials are correctly set in `.env`
- **No Text Detected**: Ensure the image contains clear text/labels
- **Quota Exceeded**: Check your Google Cloud billing/quota limits
- **Import Errors**: Confirm all dependencies are installed

## Cost Considerations

- **Gemini API**: Pay per character processed
- **Vision API**: Free tier + pay per image after limits
- Always monitor usage in Google Cloud Console

## Technologies Used

- **Streamlit**: Web app framework
- **Google Cloud Vision**: OCR service
- **Google Gemini**: AI analysis
- **Pillow**: Image processing
- **Python-dotenv**: Environment management
