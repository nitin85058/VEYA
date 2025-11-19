"""
Health Analyzer module for Industrial Equipment Analyzer
Calculates equipment health scores and generates recommendations
"""

from config import HEALTH_PENALTIES


def calculate_health_score(equipment_data, detected_damages):
    """
    Calculate comprehensive equipment health score (0-100)

    Args:
        equipment_data (dict): Equipment analysis data
        detected_damages (list): List of detected damage types

    Returns:
        int: Health score from 0-100
    """
    score = 100  # Start with perfect health

    # Deduct points for detected damages (-penalties from config)
    for damage in detected_damages:
        for damage_type, penalty in HEALTH_PENALTIES.items():
            if damage_type.lower() in damage.lower():
                score -= penalty
                break

    # Adjust based on condition assessment
    condition = equipment_data.get('condition', '').lower()

    if 'poor' in condition:
        score -= 20  # Additional penalty for poor condition
    elif 'fair' in condition:
        score -= 10  # Additional penalty for fair condition

    # Operational status impact
    operational = equipment_data.get('operational_status', '').lower()

    if 'non-functional' in operational or 'malfunctioning' in operational:
        score -= 30  # Significant penalty for non-functional status
    elif 'limited' in operational or 'intermittent' in operational:
        score -= 15  # Penalty for limited functionality

    # Equipment age consideration (if known)
    age = equipment_data.get('estimated_age', '')
    if 'old' in age.lower() and '> 15' in age:
        score -= 10  # Age-related wear and tear

    # Ensure score stays within bounds
    return max(0, min(100, score))


def generate_health_report(equipment_data, health_score, detected_damages):
    """
    Generate detailed health assessment report

    Args:
        equipment_data (dict): Complete equipment analysis
        health_score (int): Calculated health score
        detected_damages (list): Detected damage types

    Returns:
        dict: Comprehensive health report
    """
    # Determine overall health status
    if health_score >= 80:
        overall_status = "Excellent"
        risk_level = "Low"
        recommended_action = "Continue routine maintenance"
    elif health_score >= 60:
        overall_status = "Good"
        risk_level = "Low-Medium"
        recommended_action = "Schedule routine inspection"
    elif health_score >= 40:
        overall_status = "Fair"
        risk_level = "Medium"
        recommended_action = "Schedule maintenance soon"
    elif health_score >= 20:
        overall_status = "Poor"
        risk_level = "High"
        recommended_action = "Immediate attention required"
    else:
        overall_status = "Critical"
        risk_level = "Critical"
        recommended_action = "Immediate shutdown and inspection"

    # Generate detailed breakdown
    health_report = {
        "overall_health_score": health_score,
        "status": overall_status,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "breakdown": {
            "damage_impact": len(detected_damages) * 10,  # Base penalty for any damage
            "condition_assessment": "Included in score" if 'condition' in equipment_data else "Not assessed",
            "operational_impact": "Included in score" if 'operational_status' in equipment_data else "Not assessed"
        },
        "specific_issues": detected_damages,
        "recommendations": _generate_specific_recommendations(equipment_data, health_score, detected_damages),
        "next_maintenance_date": _estimate_maintenance_schedule(health_score),
        "estimated_lifespan_remaining": _estimate_remaining_lifespan(equipment_data, health_score)
    }

    return health_report


def _generate_specific_recommendations(equipment_data, health_score, detected_damages):
    """
    Generate targeted recommendations based on equipment specifics

    Args:
        equipment_data (dict): Equipment analysis data
        health_score (int): Health score
        detected_damages (list): Detected damages

    Returns:
        list: Specific recommendations
    """
    recommendations = []

    # Equipment type specific recommendations
    equipment_type = equipment_data.get('equipment_type', '').lower()

    if 'ups' in equipment_type or 'inverter' in equipment_type:
        recommendations.append("Schedule battery capacity test")
        recommendations.append("Check cooling fan operation")

    if 'transformer' in equipment_type:
        recommendations.append("Check insulation resistance")
        recommendations.append("Verify oil levels and quality")

    if 'battery' in equipment_type.lower():
        recommendations.append("Check individual cell voltages")
        recommendations.append("Test specific gravity of electrolyte")

    # Damage-specific recommendations
    damage_recommendations = {
        "burn marks": "Replace damaged components and inspect electrical connections",
        "rust": "Apply anti-corrosion treatment and check for moisture ingress",
        "loose wires": "Tighten all electrical connections and secure wire harnesses",
        "overheating": "Clean cooling surfaces and check ventilation",
        "broken display": "Replace display unit if LCD/LED indicators are critical"
    }

    for damage in detected_damages:
        for damage_type, recommendation in damage_recommendations.items():
            if damage_type.lower() in damage.lower():
                recommendations.append(recommendation)
                break

    # Health score based general recommendations
    if health_score < 60:
        recommendations.insert(0, "URGENT: Schedule professional technician inspection")
    elif health_score < 80:
        recommendations.insert(0, "Schedule preventive maintenance within 30 days")

    # Remove duplicates
    recommendations = list(set(recommendations))

    return recommendations


def _estimate_maintenance_schedule(health_score):
    """
    Estimate time to next scheduled maintenance

    Args:
        health_score (int): Current health score

    Returns:
        str: Recommended maintenance schedule
    """
    if health_score < 40:
        return "Immediate - Within 1 week"
    elif health_score < 60:
        return "Urgent - Within 2 weeks"
    elif health_score < 80:
        return "Scheduled - Within 1 month"
    else:
        return "Routine - Within 6 months"


def _estimate_remaining_lifespan(equipment_data, health_score):
    """
    Estimate remaining useful lifespan based on condition

    Args:
        equipment_data (dict): Equipment data
        health_score (int): Health score

    Returns:
        str: Estimated remaining lifespan
    """
    if health_score >= 80:
        return "5+ years (excellent condition)"
    elif health_score >= 60:
        return "2-5 years (good condition)"
    elif health_score >= 40:
        return "1-2 years (needs attention)"
    elif health_score >= 20:
        return "6-12 months (critical)"
    else:
        return "< 6 months (replacement recommended)"


def compare_equipment_health(equipment_list):
    """
    Compare multiple equipment health scores

    Args:
        equipment_list (list): List of equipment health reports

    Returns:
        dict: Comparison summary
    """
    if not equipment_list:
        return {}

    # Sort by health score
    sorted_equipment = sorted(equipment_list, key=lambda x: x['overall_health_score'], reverse=True)

    comparison = {
        "ranking": sorted_equipment,
        "summary": {
            "healthy_count": sum(1 for eq in equipment_list if eq['overall_health_score'] >= 80),
            "needs_attention_count": sum(1 for eq in equipment_list if 40 <= eq['overall_health_score'] < 80),
            "critical_count": sum(1 for eq in equipment_list if eq['overall_health_score'] < 40),
            "average_score": sum(eq['overall_health_score'] for eq in equipment_list) / len(equipment_list)
        }
    }

    return comparison
