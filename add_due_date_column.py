"""
Script para agregar la columna due_date a la tabla expenses
Ejecutar: python add_due_date_column.py
"""
import sys
from app import create_app, db
from sqlalchemy import text

print("🔄 Iniciando script de migración...")
print("📋 Verificando conexión a la base de datos...")

try:
    app = create_app()
    
    with app.app_context():
        print("✅ Conexión establecida")
        
        # Verificar si la columna ya existe
        print("🔍 Verificando si la columna 'due_date' existe...")
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='expenses' AND column_name='due_date'
        """))
        
        if result.fetchone():
            print("✅ La columna 'due_date' ya existe en la tabla 'expenses'")
            print("📋 No es necesario agregarla nuevamente")
        else:
            print("🔄 La columna 'due_date' NO existe. Agregándola...")
            # Agregar la columna due_date
            db.session.execute(text("""
                ALTER TABLE expenses 
                ADD COLUMN due_date DATE NULL
            """))
            db.session.commit()
            print("✅ Columna 'due_date' agregada exitosamente a la tabla 'expenses'")
            print("📋 La tabla 'expenses' ahora tiene 11 columnas incluyendo 'due_date'")
            
            # Verificar que se agregó correctamente
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='expenses' AND column_name='due_date'
            """))
            if result.fetchone():
                print("✅ Verificación: La columna 'due_date' está presente en la base de datos")
            else:
                print("⚠️ Advertencia: No se pudo verificar la columna después de agregarla")
                
except Exception as e:
    print(f"\n❌ Error al ejecutar el script: {e}")
    print(f"   Tipo de error: {type(e).__name__}")
    import traceback
    print("\n📋 Detalles del error:")
    traceback.print_exc()
    print("\n💡 Alternativa: Puedes ejecutar este SQL manualmente en tu base de datos:")
    print("   ALTER TABLE expenses ADD COLUMN due_date DATE NULL;")
    sys.exit(1)

print("\n✅ Script completado exitosamente")
