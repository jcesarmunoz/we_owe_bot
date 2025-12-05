"""
Script para inicializar la base de datos
Ejecutar: python init_db.py
"""
from app import create_app, db
from app.models import User, Expense

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("✅ Base de datos inicializada correctamente")
    print("📋 Tablas creadas: users, expenses")

