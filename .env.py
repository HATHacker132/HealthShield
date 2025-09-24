# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///healthshield.db

# SMS Configuration
SMS_PROVIDER=simple  # Options: twilio, fast2sms, simple
HEALTH_AUTHORITY_NUMBER=18605001066

# Twilio Configuration (if using Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Fast2SMS Configuration (if using Fast2SMS)
FAST2SMS_API_KEY=your_fast2sms_api_key