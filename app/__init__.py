"""
SmartExpenseBot - Bot de Telegram para gestión de gastos compartidos
Inicialización de la aplicación Flask
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import config

# Inicializar extensiones
db = SQLAlchemy()


def create_app(config_name="development"):
    """
    Factory function para crear la aplicación Flask

    Args:
        config_name: Nombre del entorno de configuración

    Returns:
        Flask app instance
    """
    import os

    # En Vercel, usar /tmp para instance path porque es el único directorio escribible
    if os.environ.get("VERCEL"):
        app = Flask(__name__, instance_path="/tmp/instance")
        try:
            os.makedirs(app.instance_path, exist_ok=True)
        except OSError:
            pass
    else:
        app = Flask(__name__)

    # Configurar logging mejorado
    from app.logger_config import setup_logging
    import os

    log_file = os.getenv("LOG_FILE", "app.log")
    setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"), log_file=log_file)

    # Cargar configuración
    app.config.from_object(config.get(config_name, config["default"]))

    # Inicializar extensiones
    db.init_app(app)

    # Importar modelos para que SQLAlchemy los registre (import diferido para evitar circular)
    with app.app_context():
        from app import models  # noqa: F401

    # Registrar blueprints
    from app.routes import bp

    app.register_blueprint(bp)

    # Crear tablas en la base de datos (solo si la conexión está disponible)
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        # Si hay un error de conexión, no fallar - las tablas se crearán cuando se conecte
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"No se pudo crear las tablas al inicializar: {e}")

    return app


# Crear instancia de la aplicación por defecto para compatibilidad con servidores WSGI/ASGI
# Esto permite usar: uvicorn app:app o gunicorn app:app
# La creación se hace de forma lazy para evitar errores de conexión al importar
_app_instance = None


def get_app():
    """Obtiene o crea la instancia de la aplicación (patrón singleton)"""
    global _app_instance
    if _app_instance is None:
        try:
            _app_instance = create_app()
        except Exception as e:
            # Si hay un error al crear la app (ej: configuración faltante), crear una app mínima
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Error al crear la aplicación con configuración completa: {e}"
            )
            logger.warning(
                "Creando aplicación mínima. Asegúrate de configurar las variables de entorno."
            )
            # Crear una app mínima para evitar errores de importación
            import os

            if os.environ.get("VERCEL"):
                _app_instance = Flask(__name__, instance_path="/tmp/instance")
            else:
                _app_instance = Flask(__name__)
            _app_instance.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db"
            _app_instance.config["SECRET_KEY"] = "dev-secret-key"
            _app_instance.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
            db.init_app(_app_instance)
    return _app_instance


# Crear el objeto app para compatibilidad con servidores WSGI/ASGI
# Esto permite usar: uvicorn app:app o gunicorn app:app
_flask_app = get_app()

# Crear wrapper ASGI para uvicorn
try:
    from asgiref.wsgi import WsgiToAsgi

    # Envolver la aplicación Flask en un wrapper ASGI
    app = WsgiToAsgi(_flask_app)
except ImportError:
    # Si asgiref no está disponible, usar la app Flask directamente
    # (funcionará con gunicorn pero no con uvicorn)
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        "asgiref no está instalado. Para usar uvicorn, instala: pip install asgiref"
    )
    app = _flask_app
