"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN no está configurada")
    
    # Google Gemini
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY no está configurada")
    
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    # Construir URL base de Gemini API
    _gemini_base_url = os.getenv(
        'GEMINI_API_URL',
        f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent'
    )
    GEMINI_API_URL = _gemini_base_url
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

