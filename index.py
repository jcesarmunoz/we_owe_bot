"""
Punto de entrada de la aplicación
"""
import logging
from app import create_app

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info("Iniciando SmartExpenseBot...")
    app.run(host='0.0.0.0', port=5000, debug=True)

