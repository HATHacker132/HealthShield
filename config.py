import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2025'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///healthshield.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SMS Service Configuration
    SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'twilio')  # twilio or fast2sms
    HEALTH_AUTHORITY_NUMBER = os.environ.get('HEALTH_AUTHORITY_NUMBER', '18605001066')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    SQLALCHEMY_DATABASE_URI = "postgresql://username:password@host:port/dbname"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    # Fast2SMS Configuration (Indian SMS Provider)
    FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY')
    
    # Application Settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'