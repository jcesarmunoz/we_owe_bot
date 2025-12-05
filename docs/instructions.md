# Especificaciones del Proyecto: Bot de Gastos Telegram (SmartExpenseBot) - V2

## 1. Visión General
Crear un bot de Telegram que permita a dos personas registrar gastos y deudas compartidas utilizando lenguaje natural. El backend procesará el texto del usuario utilizando la API de Gemini (Google) para extraer datos estructurados y guardarlos en una base de datos **PostgreSQL**. La autorización de usuarios se gestionará desde la base de datos.

## 2. Stack Tecnológico
* **Lenguaje:** Python 3.10+
* **Backend Framework:** Flask
* **Base de Datos:** PostgreSQL
* **ORM:** SQLAlchemy (Flask-SQLAlchemy)
* **IA / NLP:** Google Generative AI (Gemini 1.5 Flash o Pro)
* **Telegram Interface:** python-telegram-bot (o requests estándar con Webhooks)

---

## 3. Modelo de Datos (SQLAlchemy) - ⚠️ ACTUALIZADO

Necesitamos dos tablas: `User` para la autorización y `Expense` para las transacciones.

### Tabla: `User` (Nueva para gestión de autorización)
* `id`: Integer, Primary Key.
* **`telegram_id`**: BigInt/String (El ID único de Telegram del usuario. Clave principal para autorización).
* `name`: String (Nombre del usuario, ej: "Juan Pérez").
* `is_authorized`: Boolean (Para activar o desactivar el acceso, default=True).

### Tabla: `Expense`
* `id`: Integer, Primary Key.
* `created_at`: DateTime (default=datetime.utcnow).
* `description`: String (Concepto del gasto, ej: "Mantenimiento carro").
* `amount`: Float/Numeric (Monto del gasto).
* `currency`: String.
* **`payer_id`**: Integer, Foreign Key a `User.id` (ID del usuario que pagó).
* **`debtor_id`**: Integer, Foreign Key a `User.id` (ID del usuario que debe).
* `raw_text`: String (Mensaje original).
* `is_settled`: Boolean (default=False).

---

## 4. Integración con Gemini (Lógica de IA)

El bot debe enviar el mensaje del usuario a Gemini con instrucciones para actuar como un "Extractor de Entidades Financieras", devolviendo **JSON estricto**.

* **System Prompt:** Actúa como un extractor de entidades financieras. Analiza el texto para identificar el monto, la moneda y el concepto, y devuelve un JSON.
* **Output esperado:** JSON estricto.
    ```json
    {
      "amount": 500,
      "currency": "USD",
      "description": "mantenimiento carro",
      "category": "transporte",
      "action": "debt" 
    }
    ```

---

## 5. Endpoints y Flujo de Flask - ⚠️ LÓGICA ACTUALIZADA

### Ruta: `/webhook` (POST)
1.  Recibe el update de Telegram (JSON).
2.  **Lógica de Autorización (Paso Crítico):** Obtiene el `telegram_id` del remitente. **Consulta la tabla `User`**. Si el `telegram_id` existe y `is_authorized` es `True`, procede. Si no, responde: *"No estás autorizado para usar este bot."*
3.  Si está autorizado, obtiene el `id` interno del usuario (de la tabla `User`).
4.  Envía el texto del mensaje (`message.text`) a la función wrapper de Gemini.
5.  Recibe el JSON estructurado de Gemini.
6.  Instancia un objeto `Expense`, usando el `id` interno del usuario (obtenido en el paso 3) como la `payer_id` o `debtor_id` según el contexto, y lo guarda en PostgreSQL.
7.  Devuelve un mensaje de confirmación al usuario.

---

## 6. Variables de Entorno (.env) - ⚠️ SIMPLIFICADO

El código debe usar `python-dotenv` para cargar:
* `TELEGRAM_BOT_TOKEN`
* `GOOGLE_API_KEY` (Para Gemini)
* `DATABASE_URL` (Connection string de Postgres)

---

## 7. Instrucciones Adicionales
* Se requiere una ruta o comando inicial (`/start` o `/admin add`) para **poblar la tabla `User` inicialmente**.
* El código debe ser modular, separando `models.py`, `bot_services.py` y `ai_services.py`.