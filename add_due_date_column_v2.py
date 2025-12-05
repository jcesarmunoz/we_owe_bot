"""
Script para agregar la columna due_date a la tabla expenses
Ejecutar: python add_due_date_column_v2.py
"""
import sys
import os

# Redirigir salida a un archivo para debugging
log_file = open('migration_log.txt', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

try:
    print("🔄 Iniciando script de migración...")
    print("📋 Verificando conexión a la base de datos...")
    
    from app import create_app, db
    from sqlalchemy import text
    
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
    log_file.close()
    sys.exit(1)

print("\n✅ Script completado exitosamente")
log_file.close()

# También imprimir en consola
with open('migration_log.txt', 'r', encoding='utf-8') as f:
    print(f.read())

