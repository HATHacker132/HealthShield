from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

db = SQLAlchemy()

class UserReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100))
    
    # Symptoms (stored as JSON string)
    symptoms = db.Column(db.Text, nullable=False)
    
    # Analysis Results
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high
    detected_diseases = db.Column(db.Text)  # JSON string of diseases
    risk_score = db.Column(db.Float, nullable=False)
    
    # SMS Alert Info
    sms_sent = db.Column(db.Boolean, default=False)
    sms_timestamp = db.Column(db.DateTime)
    sms_recipient = db.Column(db.String(15))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'village': self.village,
            'mobile': self.mobile,
            'email': self.email,
            'symptoms': self.symptoms,
            'risk_level': self.risk_level,
            'detected_diseases': self.detected_diseases,
            'risk_score': self.risk_score,
            'sms_sent': self.sms_sent,
            'sms_timestamp': self.sms_timestamp.isoformat() if self.sms_timestamp else None,
            'created_at': self.created_at.isoformat()
        }