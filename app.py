from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, UserReport
from sms_service import SMSService
from config import Config
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Initialize SMS service
sms_service = SMSService()
# For testing, you can use SimpleSMSGateway instead:
# sms_service = SimpleSMSGateway()

# Disease database (same as frontend)
WATER_BORNE_DISEASES = [
    {
        "name": "Cholera",
        "symptoms": [2, 3, 5, 8, 9, 11],
        "description": "Acute diarrheal illness caused by infection of the intestine",
        "riskLevel": "high",
        "severity": 9
    },
    {
        "name": "Typhoid",
        "symptoms": [1, 2, 4, 8, 9],
        "description": "Bacterial infection that can spread throughout the body",
        "riskLevel": "high",
        "severity": 8
    },
    {
        "name": "Hepatitis A",
        "symptoms": [1, 4, 6, 8, 9],
        "description": "Highly contagious liver infection",
        "riskLevel": "medium",
        "severity": 6
    },
    {
        "name": "Dysentery",
        "symptoms": [2, 4, 5, 9, 11],
        "description": "Intestinal inflammation causing severe diarrhea",
        "riskLevel": "medium",
        "severity": 7
    }
]

@app.route('/')
def home():
    return jsonify({
        "message": "HealthShield Backend API",
        "version": "1.0",
        "endpoints": {
            "health_check": "/health",
            "analyze_symptoms": "/api/analyze (POST)",
            "reports": "/api/reports (GET)"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/analyze', methods=['POST'])
def analyze_symptoms():
    """
    Analyze symptoms and send SMS alert if water-borne disease detected
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'village', 'mobile', 'symptoms']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "success": False
                }), 400
        
        # Analyze symptoms for water-borne diseases
        analysis_result = analyze_symptom_data(data['symptoms'])
        
        # Create user report
        user_report = UserReport(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            village=data['village'],
            mobile=data['mobile'],
            email=data.get('email', ''),
            symptoms=json.dumps(data['symptoms']),
            risk_level=analysis_result['risk_level'],
            detected_diseases=json.dumps(analysis_result['matching_diseases']),
            risk_score=analysis_result['risk_score']
        )
        
        # Send SMS alert if high risk
        sms_sent = False
        if analysis_result['risk_level'] == 'high' and analysis_result['matching_diseases']:
            sms_sent = sms_service.send_alert(
                user_data=data,
                diseases=analysis_result['matching_diseases'],
                risk_level=analysis_result['risk_level']
            )
            
            if sms_sent:
                user_report.sms_sent = True
                user_report.sms_timestamp = datetime.utcnow()
                user_report.sms_recipient = Config.HEALTH_AUTHORITY_NUMBER
        
        # Save to database
        db.session.add(user_report)
        db.session.commit()
        
        # Prepare response
        response_data = {
            "success": True,
            "report_id": user_report.id,
            "risk_level": analysis_result['risk_level'],
            "risk_score": analysis_result['risk_score'],
            "matching_diseases": analysis_result['matching_diseases'],
            "sms_alert_sent": sms_sent,
            "message": get_result_message(analysis_result['risk_level'], sms_sent)
        }
        
        logger.info(f"Analysis completed for {data['name']} - Risk: {analysis_result['risk_level']}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in analyze_symptoms: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """
    Get all user reports (for dashboard/analytics)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        reports = UserReport.query.order_by(UserReport.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "success": True,
            "reports": [report.to_dict() for report in reports.items],
            "total": reports.total,
            "pages": reports.pages,
            "current_page": page
        })
        
    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

def analyze_symptom_data(symptoms):
    """
    Analyze symptoms and determine risk level
    """
    matching_diseases = []
    total_risk_score = 0
    
    for disease in WATER_BORNE_DISEASES:
        matched_symptoms = [s for s in disease['symptoms'] if s in symptoms]
        
        if matched_symptoms:
            match_percentage = (len(matched_symptoms) / len(disease['symptoms'])) * 100
            
            if match_percentage >= 30:  # At least 30% match
                disease_copy = disease.copy()
                disease_copy['match_percentage'] = match_percentage
                disease_copy['matched_symptoms'] = matched_symptoms
                matching_diseases.append(disease_copy)
                
                total_risk_score += disease['severity'] * (match_percentage / 100)
    
    # Determine risk level
    risk_level = "low"
    if total_risk_score >= 15:
        risk_level = "high"
    elif total_risk_score >= 8:
        risk_level = "medium"
    
    return {
        "risk_level": risk_level,
        "risk_score": total_risk_score,
        "matching_diseases": matching_diseases
    }

def get_result_message(risk_level, sms_sent):
    messages = {
        "high": f"High risk detected! {'SMS alert sent to health authorities.' if sms_sent else 'Alert system activated.'}",
        "medium": "Medium risk detected. Please consult a healthcare professional.",
        "low": "No serious water-borne disease detected. Your health appears good."
    }
    return messages.get(risk_level, "Analysis completed.")

# Database initialization
@app.before_request
def create_tables():
    if not hasattr(app,'first_request_done'):
        db.create_all()
        app.first_request_done=True

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)