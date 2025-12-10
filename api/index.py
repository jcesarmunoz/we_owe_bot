import os
import sys

# Agregar el directorio raíz al path para poder importar 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Crear la aplicación Flask
app = create_app()

# Vercel serverless function entrypoint
# Para Vercel, la variable debe llamarse 'app' (Flask)

