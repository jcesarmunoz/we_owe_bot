# Documentación de API - SmartExpenseBot

Esta documentación describe los endpoints disponibles de la API de SmartExpenseBot y cómo consumirlos.

## Base URL

```
http://localhost:8100
```

Para producción, reemplaza `localhost:8100` con tu dominio y puerto.

---

## Endpoints Disponibles

### 1. Health Check

Verifica el estado de la aplicación.

**Endpoint:** `GET /health`

**Descripción:** Retorna el estado de salud de la aplicación.

#### Request

```bash
curl -X GET http://localhost:8100/health
```

#### Response

**Status Code:** `200 OK`

```json
{
  "status": "ok",
  "message": "Bot is running"
}
```

#### Ejemplo con Python

```python
import requests

response = requests.get('http://localhost:8100/health')
print(response.json())
# Output: {'status': 'ok', 'message': 'Bot is running'}
```

---

### 2. Webhook de Telegram

Endpoint principal para recibir updates de Telegram.

**Endpoint:** `POST /webhook`

**Descripción:** Recibe updates de Telegram, procesa mensajes con IA (Gemini) y registra gastos en la base de datos.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:** JSON con el formato de update de Telegram

#### Estructura del Update de Telegram

El webhook espera recibir el formato estándar de updates de Telegram. Ejemplos:

##### Mensaje de texto normal

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Juan",
      "last_name": "Pérez",
      "username": "juanperez"
    },
    "chat": {
      "id": 123456789,
      "first_name": "Juan",
      "last_name": "Pérez",
      "username": "juanperez",
      "type": "private"
    },
    "date": 1234567890,
    "text": "Gasté 50 USD en el supermercado"
  }
}
```

##### Comando /start

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 2,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Juan",
      "last_name": "Pérez",
      "username": "juanperez"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "date": 1234567890,
    "text": "/start"
  }
}
```

##### Comando /admin

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 3,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Admin",
      "username": "admin"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "date": 1234567890,
    "text": "/admin list"
  }
}
```

#### Response

**Status Code:** `200 OK` (siempre retorna 200 para evitar reintentos de Telegram)

```json
{
  "status": "ok"
}
```

**Status Code:** `400 Bad Request` (si el update está vacío)

```json
{
  "status": "error",
  "message": "Empty update"
}
```

**Status Code:** `500 Internal Server Error` (si hay un error interno)

```json
{
  "status": "error",
  "message": "Error description"
}
```

#### Flujo de Procesamiento

1. **Recepción del Update:** El endpoint recibe el update de Telegram
2. **Extracción de Datos:** Extrae `telegram_id` y `message_text` del update
3. **Manejo de Comandos Especiales:**
   - `/start` - Registra un nuevo usuario
   - `/admin <comando>` - Ejecuta comandos de administración
4. **Verificación de Autorización:** Verifica si el usuario está autorizado
5. **Procesamiento con IA:** Si es un mensaje de gasto, lo procesa con Gemini
6. **Registro en Base de Datos:** Guarda el gasto en la base de datos
7. **Confirmación:** Envía un mensaje de confirmación al usuario vía Telegram

#### Ejemplos de Uso

##### Ejemplo 1: Registrar un gasto

```bash
curl -X POST http://localhost:8100/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "Juan",
        "last_name": "Pérez",
        "username": "juanperez"
      },
      "chat": {
        "id": 123456789,
        "type": "private"
      },
      "date": 1234567890,
      "text": "Gasté 50 USD en el supermercado"
    }
  }'
```

##### Ejemplo 2: Comando /start

```bash
curl -X POST http://localhost:8100/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 2,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "Juan",
        "username": "juanperez"
      },
      "chat": {
        "id": 123456789,
        "type": "private"
      },
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

##### Ejemplo 3: Comando /admin list

```bash
curl -X POST http://localhost:8100/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 3,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "Admin"
      },
      "chat": {
        "id": 123456789,
        "type": "private"
      },
      "date": 1234567890,
      "text": "/admin list"
    }
  }'
```

#### Ejemplo con Python

```python
import requests
import json

# URL del webhook
url = "http://localhost:8100/webhook"

# Update de Telegram simulado
update = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Juan",
            "last_name": "Pérez",
            "username": "juanperez"
        },
        "chat": {
            "id": 123456789,
            "type": "private"
        },
        "date": 1234567890,
        "text": "Gasté 50 USD en el supermercado"
    }
}

# Enviar request
response = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json=update
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
```

#### Ejemplo con JavaScript/Node.js

```javascript
const axios = require('axios');

const url = 'http://localhost:8100/webhook';

const update = {
  update_id: 123456789,
  message: {
    message_id: 1,
    from: {
      id: 123456789,
      is_bot: false,
      first_name: 'Juan',
      last_name: 'Pérez',
      username: 'juanperez'
    },
    chat: {
      id: 123456789,
      type: 'private'
    },
    date: 1234567890,
    text: 'Gasté 50 USD en el supermercado'
  }
};

axios.post(url, update)
  .then(response => {
    console.log('Status Code:', response.status);
    console.log('Response:', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

---

## Comandos del Bot

El bot reconoce los siguientes comandos cuando se envían a través del webhook:

### `/start`

Registra un nuevo usuario en el sistema.

**Uso:** Enviar un mensaje con texto `/start`

**Respuesta del Bot:**
- Si el usuario es nuevo: Mensaje de bienvenida con instrucciones
- Si el usuario ya existe: Mensaje de saludo confirmando que ya está registrado

### `/admin`

Comandos de administración del bot.

#### `/admin add <telegram_id> <nombre>`

Agrega un nuevo usuario manualmente.

**Ejemplo:** `/admin add 987654321 María García`

#### `/admin list`

Lista todos los usuarios registrados con su estado de autorización.

**Ejemplo:** `/admin list`

#### `/admin authorize <telegram_id>`

Autoriza un usuario para usar el bot.

**Ejemplo:** `/admin authorize 987654321`

#### `/admin deauthorize <telegram_id>`

Desautoriza un usuario, impidiéndole usar el bot.

**Ejemplo:** `/admin deauthorize 987654321`

---

## Mensajes de Gasto

El bot procesa mensajes en lenguaje natural para registrar gastos. Ejemplos:

- "Gasté 50 USD en el supermercado"
- "Pagué 30 dólares por el taxi"
- "Compré comida por 25 USD"
- "Gastamos 100 USD en restaurante"

El bot utiliza Google Gemini para extraer:
- **Monto:** Cantidad del gasto
- **Moneda:** Código de moneda (USD, EUR, etc.)
- **Descripción:** Concepto del gasto
- **Categoría:** Categoría del gasto (opcional)
- **Acción:** Tipo de acción (debt o expense)

---

## Configuración del Webhook en Telegram

Para que Telegram envíe updates a tu servidor, debes configurar el webhook:

```bash
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://tu-dominio.com/webhook"
```

Para desarrollo local con ngrok:

```bash
# 1. Iniciar ngrok
ngrok http 8100

# 2. Configurar webhook con la URL de ngrok
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://tu-url-ngrok.ngrok.io/webhook"
```

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200    | OK - Request procesado correctamente |
| 400    | Bad Request - Update vacío o formato inválido |
| 500    | Internal Server Error - Error en el servidor |

---

## Manejo de Errores

Todos los endpoints retornan JSON con la siguiente estructura en caso de error:

```json
{
  "status": "error",
  "message": "Descripción del error"
}
```

### Errores Comunes

1. **Usuario no autorizado:**
   - El bot envía un mensaje al usuario vía Telegram
   - El endpoint retorna `200 OK` para evitar reintentos

2. **Usuario no registrado:**
   - El bot envía un mensaje indicando que use `/start`
   - El endpoint retorna `200 OK`

3. **Error al procesar mensaje:**
   - El bot envía un mensaje de error al usuario
   - El endpoint retorna `200 OK`

4. **Error de conexión a base de datos:**
   - Se registra en los logs
   - El endpoint retorna `500 Internal Server Error`

---

## Notas Importantes

1. **Siempre retorna 200 OK:** El endpoint `/webhook` siempre intenta retornar `200 OK` para evitar que Telegram reintente el envío. Los errores se manejan internamente y se comunican al usuario vía Telegram.

2. **Formato de Update:** El webhook espera recibir el formato estándar de updates de Telegram. Asegúrate de que tu cliente envíe el formato correcto.

3. **Autorización:** Todos los usuarios deben estar registrados y autorizados antes de poder registrar gastos.

4. **Procesamiento Asíncrono:** El procesamiento con Gemini puede tomar algunos segundos. El endpoint retorna inmediatamente mientras procesa en segundo plano.

5. **Base de Datos:** Se requieren al menos 2 usuarios registrados para poder registrar gastos (uno que paga y otro que debe).

---

## Ejemplos Completos

### Flujo Completo: Registrar un Gasto

1. **Usuario envía mensaje en Telegram:** "Gasté 50 USD en el supermercado"
2. **Telegram envía update al webhook:**
   ```json
   {
     "update_id": 123,
     "message": {
       "from": {"id": 123456789},
       "text": "Gasté 50 USD en el supermercado"
     }
   }
   ```
3. **API procesa el mensaje con Gemini**
4. **API guarda el gasto en la base de datos**
5. **API envía confirmación al usuario vía Telegram**
6. **API retorna respuesta al webhook de Telegram**

### Testing Local

Para probar localmente sin configurar Telegram:

```python
import requests
import json

# Simular update de Telegram
test_update = {
    "update_id": 1,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456789,
            "is_bot": False,
            "first_name": "Test",
            "username": "testuser"
        },
        "chat": {
            "id": 123456789,
            "type": "private"
        },
        "date": 1234567890,
        "text": "Gasté 50 USD en el supermercado"
    }
}

response = requests.post(
    "http://localhost:8100/webhook",
    json=test_update,
    headers={"Content-Type": "application/json"}
)

print(json.dumps(response.json(), indent=2))
```

---

## Soporte

Para más información sobre la estructura del proyecto, consulta:
- `docs/instructions.md` - Especificaciones del proyecto
- `README.md` - Documentación general

