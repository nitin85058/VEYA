"""
UI Components module for Industrial Equipment Analyzer
Provides reusable Streamlit components and helpers
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from config import SystemSettings, HEALTH_PENALTIES, DAMAGE_TYPES
import json


def display_equipment_analysis_results(equipment_data, health_score, detected_damages):
    """
    Display comprehensive equipment analysis results

    Args:
        equipment_data (dict): Parsed equipment data
        health_score (int): Health score 0-100
        detected_damages (list): Detected damage types
    """
    # Enhanced display
    st.header("📊 Analysis Results")

    # Summary metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏥 Health Score", f"{health_score}%")
    with col2:
        equipment_type = equipment_data.get('equipment_type', 'Unknown')
        st.metric("🔧 Equipment Type", equipment_type)
    with col3:
        confidence = equipment_data.get('confidence', 'medium').title()
        st.metric("🎯 Confidence", confidence)

    # Detailed equipment information
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Equipment Details")
        display_equipment_details(equipment_data)

    with col2:
        st.subheader("🏥 Condition & Status")
        display_condition_status(equipment_data)

        # Damage section
        if detected_damages:
            st.subheader("🔧 Detected Damage/Faults")
            display_damage_list(detected_damages)
        else:
            st.success("✅ No damage detected")

    # Specifications
    display_specifications(equipment_data)

    # Export options
    display_export_options(equipment_data, health_score, detected_damages)


def display_equipment_details(equipment_data):
    """Display basic equipment identification information"""
    details = [
        ("🏭 Manufacturer", equipment_data.get('manufacturer', 'Unknown')),
        ("📦 Model", equipment_data.get('model_number', 'Unknown')),
        ("🔢 Serial", equipment_data.get('serial_number', 'Unknown'))
    ]

    for label, value in details:
        st.write(f"**{label}:** {value}")


def display_condition_status(equipment_data):
    """Display condition and operational status with color coding"""
    condition = equipment_data.get('condition', 'Unknown')
    operational = equipment_data.get('operational_status', 'Unknown')

    # Condition indicator
    if 'good' in condition.lower() or 'new' in condition.lower():
        st.success(f"🟢 **Condition:** {condition}")
    elif 'fair' in condition.lower():
        st.warning(f"🟡 **Condition:** {condition}")
    else:
        st.error(f"🔴 **Condition:** {condition}")

    # Operational status
    st.write(f"**⚙️ Operational Status:** {operational}")


def display_damage_list(detected_damages):
    """Display list of detected damages"""
    for damage in detected_damages:
        st.error(f"• {damage}")


def display_specifications(equipment_data):
    """Display technical specifications"""
    specs = equipment_data.get('specifications', {})

    if specs:
        st.subheader("⚙️ Technical Specifications")

        # Create a more organized display
        spec_items = []
        for key, value in specs.items():
            if value and value != 'string':  # Filter out empty/unset values
                formatted_key = key.replace('_', ' ').title()
                spec_items.append(f"**{formatted_key}:** {value}")

        if spec_items:
            cols = st.columns(min(2, len(spec_items)))
            for i, spec in enumerate(spec_items):
                cols[i % 2].write(spec)
        else:
            st.write("*No specifications extracted*")
    else:
        st.write("*No specifications found*")


def display_export_options(equipment_data, health_score, detected_damages):
    """Display export/download options for analysis results"""
    import json

    st.subheader("💾 Export Reports")

    col1, col2 = st.columns(2)

    with col1:
        # JSON export
        json_data = {
            "equipment_data": equipment_data,
            "health_score": health_score,
            "detected_damages": detected_damages,
            "compliance_check": getattr(equipment_data, 'compliance', {}),
            "analysis_timestamp": pd.Timestamp.now().isoformat()
        }

        json_str = json.dumps(json_data, indent=2)
        equipment_name = equipment_data.get('equipment_type', 'Equipment').replace('/', '_')
        file_name = f"{equipment_name}_analysis.json"

        st.download_button(
            label="📥 Download JSON Report",
            data=json_str,
            file_name=file_name,
            mime="application/json"
        )

    with col2:
        # Health report text file
        report_content = generate_health_report_text(equipment_data, health_score, detected_damages)
        equipment_name = equipment_data.get('equipment_type', 'Equipment').replace('/', '_')

        st.download_button(
            label="📄 Download Health Report",
            data=report_content,
            file_name=f"{equipment_name}_health_report.txt",
            mime="text/plain"
        )


def generate_health_report_text(equipment_data, health_score, detected_damages):
    """Generate human-readable health report text"""
    equipment_type = equipment_data.get('equipment_type', 'Unknown')
    manufacturer = equipment_data.get('manufacturer', 'Unknown')
    model = equipment_data.get('model_number', 'Unknown')
    serial = equipment_data.get('serial_number', 'Unknown')
    condition = equipment_data.get('condition', 'Unknown')

    report = f"""INDUSTRIAL EQUIPMENT HEALTH ANALYSIS REPORT
{'='*50}

EQUIPMENT INFORMATION:
- Type: {equipment_type}
- Manufacturer: {manufacturer}
- Model: {model}
- Serial Number: {serial}

HEALTH ASSESSMENT:
- Overall Health Score: {health_score}%
- Condition: {condition}
- Damages Detected: {', '.join(detected_damages) if detected_damages else 'None'}

TECHNICAL SPECIFICATIONS:
"""

    specs = equipment_data.get('specifications', {})
    for key, value in specs.items():
        if value and value != 'string':
            report += f"- {key.replace('_', ' ').title()}: {value}\n"

    report += "\nRECOMMENDATIONS:\n"

    if health_score < 40:
        report += "- CRITICAL: Immediate professional inspection required\n"
        report += "- Consider equipment replacement if cost of repair > 50% of new equipment\n"
    elif health_score < 60:
        report += "- URGENT: Schedule repair within 1 week\n"
        report += "- Address all detected damages before further use\n"
    elif health_score < 80:
        report += "- ATTENTION: Schedule maintenance within 30 days\n"
        report += "- Monitor condition during next usage cycle\n"
    else:
        report += "- GOOD: Continue routine maintenance schedule\n"
        report += "- Equipment in good operational condition\n"

    report += f"\nReport Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return report


def display_loading_message(stage, progress):
    """Display progress message during processing"""
    progress_messages = {
        "classification": "🤖 Analyzing equipment type...",
        "damage_detection": "👀 Scanning for physical damage...",
        "ocr": "📝 Extracting text from image...",
        "analysis": "🔬 Processing with AI analysis...",
        "health_calculation": "📊 Calculating health score..."
    }

    if stage in progress_messages:
        with st.spinner(progress_messages[stage]):
            st.write(f"**{progress}/5 steps completed**")


def create_equipment_summary_card(equipment_data, health_score, detected_damages):
    """
    Create a summary card for equipment overview
    Helper for multi-equipment dashboards
    """
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            equipment_type = equipment_data.get('equipment_type', 'Unknown')
            st.metric("Type", equipment_type)

        with col2:
            manufacturer = equipment_data.get('manufacturer', 'Unknown')
            st.metric("Manufacturer", manufacturer)

        with col3:
            st.metric("Health Score", f"{health_score}%")

        with col4:
            if detected_damages:
                st.metric("Issues", len(detected_damages))
            else:
                st.metric("Status", "✅ Good")


def display_health_score_gauge(health_score):
    """Display an interactive health score gauge using Plotly"""
    if health_score >= 80:
        color = "#00ff00"  # Green
        status_text = "Excellent"
    elif health_score >= 60:
        color = "#90ed3d"  # Light green
        status_text = "Good"
    elif health_score >= 40:
        color = "#ffff00"  # Yellow
        status_text = "Fair"
    elif health_score >= 20:
        color = "#ff8c00"  # Orange
        status_text = "Poor"
    else:
        color = "#ff0000"  # Red
        status_text = "Critical"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Equipment Health Score<br><span style='font-size:0.8em;color:gray'>{status_text}</span>", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': 'lightcoral'},
                {'range': [40, 60], 'color': 'lightsalmon'},
                {'range': [60, 80], 'color': 'lightgreen'},
                {'range': [80, 100], 'color': 'limegreen'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))

    st.plotly_chart(fig, use_container_width=True)


def display_damage_impact_chart(detected_damages):
    """Display a chart showing damage impact on health score"""
    from config import HEALTH_PENALTIES

    if not detected_damages:
        st.info("✅ No damages detected - equipment in optimal condition!")
        return

    # Calculate impact for each damage type
    damage_impacts = []
    total_impact = 0

    for damage in detected_damages:
        impact = 0
        for damage_type, penalty in HEALTH_PENALTIES.items():
            if damage_type.lower() in damage.lower():
                impact = penalty
                break
        damage_impacts.append((damage, impact))
        total_impact += impact

    # Create impact chart
    damages_only = [d[0] for d in damage_impacts]
    impacts_only = [d[1] for d in damage_impacts]

    fig = px.bar(
        x=damages_only,
        y=impacts_only,
        title=f"Damage Impact Analysis (Total: -{total_impact} points)",
        labels={'x': 'Damage Type', 'y': 'Health Score Impact'},
        color=impacts_only,
        color_continuous_scale='Reds'
    )

    fig.update_layout(
        xaxis_title="Detected Damage Types",
        yaxis_title="Health Score Reduction",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def display_equipment_health_trend(health_score):
    """Display a simulated health trend chart to show potential degradation"""
    # Generate simulated historical data based on current score
    import random

    # Simulate last 12 months of health scores
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Start with higher scores in the past, gradually decline to current
    base_score = min(95, health_score + random.randint(5, 15))

    historical_scores = []
    for i in range(12):
        if i < 9:  # First 9 months higher
            score = base_score - random.randint(0, 5) - (i * 1)  # Gradual decline
        else:  # Last 3 months current level
            score = health_score + random.randint(-3, 3)

        score = max(10, min(100, score))  # Keep within bounds
        historical_scores.append(score)

    # Add current analysis
    historical_scores.append(health_score)
    months.append("Current")

    # Create trend line chart
    fig = px.line(
        x=months,
        y=historical_scores,
        title="Equipment Health Trend (Simulated)",
        labels={'x': 'Month', 'y': 'Health Score'},
        markers=True
    )

    # Add reference lines
    fig.add_hline(y=80, line_dash="dash", line_color="green",
                 annotation_text="Excellent", annotation_position="top right")
    fig.add_hline(y=60, line_dash="dash", line_color="yellow",
                 annotation_text="Good", annotation_position="bottom right")

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def display_equipment_comparative_analysis():
    """Display comparative analysis dashboard for multiple equipment"""
    st.header("📊 Comparative Equipment Analysis")

    # Mock data for demonstration
    sample_equipment = [
        {"name": "Main UPS", "type": "UPS / Inverter", "manufacturer": "Siemens",
         "health_score": 85, "damages": [], "last_inspection": "2024-03-15"},
        {"name": "Backup Transformer", "type": "Transformer", "manufacturer": "ABB",
         "health_score": 72, "damages": ["rust", "loose wires"], "last_inspection": "2024-02-28"},
        {"name": "Control Panel A", "type": "Breaker Panel", "manufacturer": "Rockwell",
         "health_score": 45, "damages": ["burn marks", "mechanical damage"], "last_inspection": "2024-01-20"},
        {"name": "Power Meter", "type": "Meter / Gauge", "manufacturer": "GE",
         "health_score": 90, "damages": [], "last_inspection": "2024-03-10"}
    ]

    # Health score comparison bar chart
    equipment_names = [eq['name'] for eq in sample_equipment]
    health_scores = [eq['health_score'] for eq in sample_equipment]

    fig_bar = px.bar(
        x=equipment_names,
        y=health_scores,
        title="Equipment Health Comparison",
        color=health_scores,
        color_continuous_scale=['red', 'yellow', 'green']
    )
    fig_bar.update_layout(xaxis_title="Equipment", yaxis_title="Health Score")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Summary statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_score = sum(health_scores) / len(health_scores)
        st.metric("Average Health Score", f"{avg_score:.1f}")

    with col2:
        critical_count = sum(1 for score in health_scores if score < 50)
        st.metric("Critical Equipment", critical_count)

    with col3:
        good_count = sum(1 for score in health_scores if score >= 80)
        st.metric("Healthy Equipment", good_count)

    # Detailed table view
    st.subheader("📋 Equipment Details")

    table_data = []
    for eq in sample_equipment:
        table_data.append({
            "Equipment": eq['name'],
            "Type": eq['type'],
            "Manufacturer": eq['manufacturer'],
            "Health Score": f"{eq['health_score']}%",
            "Issues": len(eq['damages']),
            "Last Inspection": eq['last_inspection']
        })

    st.dataframe(table_data, use_container_width=True)


def display_maintenance_dashboard(health_score, detected_damages):
    """Display a comprehensive maintenance and risk assessment dashboard"""
    st.header("🛠️ Maintenance & Risk Dashboard")

    # Risk assessment section
    col1, col2, col3 = st.columns(3)

    with col1:
        if health_score >= 80:
            st.success("🟢 **Risk Level: Low**")
            risk_level = "Low"
        elif health_score >= 60:
            st.warning("🟡 **Risk Level: Medium**")
            risk_level = "Medium"
        elif health_score >= 30:
            st.error("🟠 **Risk Level: High**")
            risk_level = "High"
        else:
            st.error("🔴 **Risk Level: Critical**")
            risk_level = "Critical"

    with col2:
        if health_score >= 80:
            maint_priority = "Routine (6 months)"
        elif health_score >= 60:
            maint_priority = "Schedule (1 month)"
        elif health_score >= 40:
            maint_priority = "Priority (2 weeks)"
        else:
            maint_priority = "Immediate (1 week)"

        st.metric("🔧 Maintenance Priority", maint_priority)

    with col3:
        st.metric("⚠️ Active Issues", len(detected_damages))

    # Recommendations table
    st.subheader("📋 Recommended Actions")

    recommendations = []
    if len(detected_damages) > 0:
        recommendations.append({"Priority": "High", "Action": "Inspect and repair all detected damages", "Timeline": "Immediate"})
    if health_score < 60:
        recommendations.append({"Priority": "High", "Action": "Complete system diagnostics", "Timeline": "Within 1 week"})
    if health_score < 40:
        recommendations.append({"Priority": "Critical", "Action": "Consider equipment replacement", "Timeline": "Evaluate immediately"})
    else:
        recommendations.append({"Priority": "Routine", "Action": "Continue preventive maintenance", "Timeline": "6 months"})

    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(rec_df, use_container_width=True)
    else:
        st.success("✅ No immediate actions required")


def display_feature_overview():
    """Display available analysis features"""
    from config import SystemSettings

    st.header("🎯 Available Analysis Features")

    cols = st.columns(3)
    for i, (title, description) in enumerate(SystemSettings.FEATURE_OVERVIEW):
        with cols[i % 3]:
            st.subheader(title)
            st.write(description)
