"""
Main Application Entry Point for Industrial Equipment Analyzer
Orchestrates the complete analysis pipeline using modular components
"""

import streamlit as st
import os
from config import SystemSettings, APIConfig
from vision_ocr import extract_text_from_image
from ai_classifier import classify_equipment_type, detect_damage_and_faults
from data_parser import parse_equipment_data
from health_analyzer import calculate_health_score
from ui_components import (
    display_equipment_analysis_results,
    display_loading_message,
    display_feature_overview,
    create_equipment_summary_card,
    display_health_score_gauge,
    display_damage_impact_chart,
    display_equipment_health_trend,
    display_equipment_comparative_analysis,
    display_maintenance_dashboard
)

def main():
    """Main application function"""
    # Set page title
    st.set_page_config(
        page_title="Industrial Equipment Analyzer",
        page_icon="🚀",
        layout="wide"
    )

    # Title and header
    st.title(SystemSettings.TITLE)

    # Sidebar configuration
    st.sidebar.header("📤 Upload Equipment Image")

    # Validate API keys on startup
    validation_issues = APIConfig.validate_credentials()
    if validation_issues:
        st.sidebar.error("⚠️ API Configuration Required")
        with st.sidebar.expander("Setup Instructions"):
            st.write("Please configure your API keys in the `.env` file:")
            for issue in validation_issues:
                st.write(f"• {issue}")

            st.write("\n**Required API Keys:**")
            st.code("""
GENAI_API_KEY=your_gemini_api_key_here
VISION_API_KEY=your_vision_api_key_here
""")

    # File upload section
    uploaded_file = st.sidebar.file_uploader(
        "Choose an image...", 
        type=SystemSettings.ALLOWED_EXTENSIONS
    )

    # Main content area
    if uploaded_file is not None:
        # Display uploaded image
        image = st.sidebar.image(uploaded_file, caption='📸 Uploaded Equipment Image', use_column_width=True)

        # Analysis button
        if st.sidebar.button("🔍 Analyze Equipment", type="primary"):
            run_equipment_analysis(uploaded_file)

    else:
        # Welcome screen with feature overview
        st.info("👈 **Get started:** Upload an equipment image using the sidebar to begin AI-powered analysis!")
        display_feature_overview()

        # Display sample workflow
        st.header("📋 Analysis Workflow")

        workflow_steps = [
            ("📤 Image Upload", "Upload industrial equipment photo"),
            ("🎯 AI Classification", "Automatically identify equipment type"),
            ("🔍 Damage Detection", "Scan for physical damage and faults"),
            ("📝 OCR Processing", "Extract text and specifications"),
            ("🧠 Deep Analysis", "AI-powered condition assessment"),
            ("📊 Health Scoring", "Calculate comprehensive health score"),
            ("📈 Risk Assessment", "Generate maintenance recommendations"),
            ("💾 Report Export", "Download detailed analysis reports")
        ]

        cols = st.columns(4)
        for i, (title, description) in enumerate(workflow_steps):
            with cols[i % 4]:
                st.subheader(f"{i+1}. {title}")
                st.write(description)


def run_equipment_analysis(uploaded_file):
    """
    Execute the complete equipment analysis pipeline

    Args:
        uploaded_file: Streamlit uploaded file object
    """
    try:
        # Check API validation before processing
        validation_issues = APIConfig.validate_credentials()
        if validation_issues:
            st.error("🚫 API configuration required before analysis. Please check sidebar setup.")
            return

        # Save uploaded file temporarily
        temp_path = SystemSettings.TEMP_IMAGE_FILE
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        st.header("🔄 Analysis in Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Equipment Classification
        progress_bar.progress(20)
        status_text.text("Step 1/5: Classifying equipment type...")
        with st.spinner("🤖 Analyzing equipment type..."):
            equipment_type = classify_equipment_type(temp_path)

        st.success(f"🎯 **Equipment Classification:** **{equipment_type}**")
        progress_bar.progress(40)

        # Step 2: Damage Detection
        status_text.text("Step 2/5: Scanning for physical damage...")
        with st.spinner("👀 Scanning for physical damage..."):
            detected_damages = detect_damage_and_faults(temp_path, equipment_type)

        if detected_damages:
            st.warning(f"⚠️ **Damages Detected:** {', '.join(detected_damages)}")
        else:
            st.success("✅ **No visible damage detected**")

        progress_bar.progress(60)

        # Step 3: OCR Processing
        status_text.text("Step 3/5: Extracting text from image...")
        with st.spinner("📝 Extracting text from image..."):
            ocr_text = extract_text_from_image(temp_path)

        if ocr_text:
            st.success("✅ Text extraction completed!")
            with st.expander("📋 Extracted Text"):
                st.code(ocr_text, language="text")
        else:
            st.warning("⚠️ No text detected in image")

        progress_bar.progress(80)

        # Step 4: AI Analysis & Data Parsing
        status_text.text("Step 4/5: AI-powered equipment analysis...")
        with st.spinner("🔬 Processing with AI analysis..."):
            equipment_data = parse_equipment_data(ocr_text, equipment_type, detected_damages)

        if "error" not in equipment_data:
            st.success("✅ Analysis pipeline completed!")
        else:
            st.error("❌ Analysis failed")

        # Step 5: Health Score Calculation
        status_text.text("Step 5/5: Calculating health score...")
        with st.spinner("📊 Calculating health score..."):
            health_score = calculate_health_score(equipment_data, detected_damages)

        progress_bar.progress(100)

        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Display results using UI components
        display_equipment_analysis_results(equipment_data, health_score, detected_damages)

        # Phase 2: Smart Analytics Dashboard
        display_phase2_analytics(health_score, detected_damages, equipment_data)

        # Additional analysis sections
        display_additional_analysis(equipment_data)

        # Cleanup temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        # Cleanup on error
        if os.path.exists(SystemSettings.TEMP_IMAGE_FILE):
            os.remove(SystemSettings.TEMP_IMAGE_FILE)


def display_additional_analysis(equipment_data):
    """Display additional analysis sections like compliance and age estimation"""
    st.header("🔍 Advanced Analysis")

    # Compliance Check
    if st.button("📋 Check Compliance Standards"):
        display_compliance_analysis(equipment_data)

    # Age Estimation
    if st.button("📊 Estimate Equipment Age"):
        display_age_estimation(equipment_data)


def display_compliance_analysis(equipment_data):
    """Display compliance check results"""
    from ai_classifier import analyze_compliance

    st.subheader("🏛️ Compliance Analysis")

    ocr_text = equipment_data.get('extracted_text', '')
    equipment_type = equipment_data.get('equipment_type', 'Unknown')

    compliance_data = analyze_compliance('', ocr_text, equipment_type)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Certification Status")
        checks = [
            ("ISO Certification", compliance_data.get('iso_certified', False)),
            ("CE Mark", compliance_data.get('ce_marked', False)),
            ("RoHS Compliant", compliance_data.get('rohs_compliant', False)),
            ("BIS Certified", compliance_data.get('bis_certified', False)),
            ("UL Listed", compliance_data.get('ul_listed', False))
        ]

        for check_name, status in checks:
            if status:
                st.success(f"✅ {check_name}")
            else:
                st.info(f"ℹ️ {check_name} - Not detected")

    with col2:
        st.subheader("Compliance Summary")
        found_certs = compliance_data.get('certifications_found', [])

        if found_certs:
            st.write("**Detected Certifications:**")
            for cert in found_certs:
                st.write(f"• {cert}")
        else:
            st.warning("⚠️ No compliance certifications detected in image")

        if compliance_data.get('potential_issues'):
            st.write("**Potential Issues:**")
            for issue in compliance_data['potential_issues']:
                st.error(f"• {issue}")


def display_age_estimation(equipment_data):
    """Display equipment age estimation"""
    from ai_classifier import detect_equipment_age

    st.subheader("📅 Equipment Age Estimation")

    ocr_text = equipment_data.get('extracted_text', '')

    age_data = detect_equipment_age('', ocr_text)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Estimated Age", age_data.get('estimated_age', 'Unknown'))
        st.metric("Confidence Level", age_data.get('confidence', 'None'))

    with col2:
        indicators = age_data.get('indicators', [])
        if indicators:
            st.write("**Technology Indicators Detected:**")
            for indicator in indicators:
                st.write(f"• {indicator}")
        else:
            st.write("*No specific technology indicators found*")


def display_phase2_analytics(health_score, detected_damages, equipment_data):
    """Display Phase 2: Smart Analytics Dashboard"""
    st.header("📊 Smart Analytics Dashboard")

    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Health Metrics", "🔧 Damage Analysis", "📈 Health Trends",
        "🔄 Comparative View", "🛠️ Maintenance Dashboard"
    ])

    with tab1:
        st.subheader("🏥 Advanced Health Metrics")

        # Health Score Gauge
        col1, col2 = st.columns([2, 1])
        with col1:
            display_health_score_gauge(health_score)

        with col2:
            # Health score breakdown
            st.markdown("### Health Score Components")
            base_health = 100

            # Calculate individual component scores
            condition_penalty = 0
            if equipment_data.get('condition', '').lower() in ['poor', 'fair']:
                condition_penalty = 20

            damage_penalty = sum(
                10 for damage in detected_damages  # Base penalty for any damage
            )

            operational_penalty = 0
            if 'non-functional' in equipment_data.get('operational_status', '').lower():
                operational_penalty = 30

            final_score = base_health - condition_penalty - damage_penalty - operational_penalty

            score_components = {
                "Base Health": base_health,
                "Condition Impact": -condition_penalty,
                "Damage Impact": -damage_penalty,
                "Operational Impact": -operational_penalty,
                "Final Score": max(0, final_score)
            }

            for component, value in score_components.items():
                st.write(f"**{component}:** {value}")

    with tab2:
        st.subheader("🔧 Damage Impact Analysis")

        # Damage chart if damages exist
        display_damage_impact_chart(detected_damages)

        # Damage details
        if detected_damages:
            st.markdown("### Damage Details")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Detected Issues:**")
                for damage in detected_damages:
                    st.error(f"• {damage}")

            with col2:
                st.write("**Impact Severity:**")
                for damage in detected_damages:
                    from config import HEALTH_PENALTIES
                    impact = 0
                    for damage_type, penalty in HEALTH_PENALTIES.items():
                        if damage_type.lower() in damage.lower():
                            impact = penalty
                            break

                    if impact >= 25:
                        st.error(f"• {damage}: High ({-impact} pts)")
                    elif impact >= 15:
                        st.warning(f"• {damage}: Medium ({-impact} pts)")
                    else:
                        st.info(f"• {damage}: Low ({-impact} pts)")
        else:
            st.success("✅ No damage detected - equipment in excellent condition!")

    with tab3:
        st.subheader("📈 Health Trend Analysis")

        # Health trend chart
        display_equipment_health_trend(health_score)

        # Trend insights
        st.markdown("### Trend Insights")
        if health_score >= 80:
            st.success("📈 Equipment health is stable and excellent.")
            st.info("💡 Continue preventive maintenance every 6 months.")
        elif health_score >= 60:
            st.info("📊 Equipment health is trending toward attention zone.")
            st.info("💡 Schedule inspection within the next month.")
        elif health_score >= 40:
            st.warning("📉 Equipment health requires immediate attention.")
            st.warning("💡 Plan repairs within the next 2 weeks.")
        else:
            st.error("📉 Equipment health is critical - immediate action required.")
            st.error("💡 Schedule emergency maintenance within 1 week.")

    with tab4:
        st.subheader("🔄 Equipment Comparative Analysis")

        # Comparative dashboard
        display_equipment_comparative_analysis()

        st.info("📋 **Note:** This shows sample equipment data for demonstration. In production, this would show your actual equipment inventory.")

    with tab5:
        st.subheader("🛠️ Maintenance & Risk Management")

        # Maintenance dashboard
        display_maintenance_dashboard(health_score, detected_damages)

        # Cost estimation
        st.markdown("### 💰 Cost Estimation")
        if health_score < 40:
            st.error("**High Risk** - Replacement recommended")
            st.write("Estimated replacement cost: $1,500 - $3,000")
        elif health_score < 60:
            st.warning("**Medium Risk** - Major repairs needed")
            st.write("Estimated repair cost: $500 - $1,500")
        elif health_score < 80:
            st.info("**Low Risk** - Minor maintenance")
            st.write("Estimated maintenance cost: $100 - $500")
        else:
            st.success("**Very Low Risk** - Routine maintenance")
            st.write("Estimated maintenance cost: $50 - $150")


if __name__ == "__main__":
    main()
