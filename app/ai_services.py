"""
Servicios de IA para integración con Google Gemini
"""
import json
import logging
from typing import Dict, Optional
import requests
from app.config import Config
from app.logger_config import log_operation, log_error, ErrorCodes

logger = logging.getLogger(__name__)

# Configuración de Gemini desde archivo de configuración
GEMINI_API_URL = Config.GEMINI_API_URL
GEMINI_API_KEY = Config.GOOGLE_API_KEY
GEMINI_MODEL = Config.GEMINI_MODEL


def extract_expense_data(text: str) -> Optional[Dict]:
    """
    Extrae datos estructurados de un mensaje de texto usando Gemini
    
    Args:
        text: Texto del mensaje del usuario
        
    Returns:
        Diccionario con los datos extraídos o None si hay error
        
    Raises:
        Exception: Si hay error en la comunicación con Gemini
    """
    try:
        # System prompt para extracción de entidades financieras
        system_prompt = """Actúa como un extractor de entidades financieras. 
Analiza el texto del usuario para identificar:
- El monto del gasto (amount)
- La moneda (currency) - por defecto COP si no se especifica
- El concepto/descripción del gasto (description)
- La categoría del gasto (category) - ej: transporte, comida, servicios, etc.
- La acción (action) - puede ser "debt" (deuda) o "expense" (gasto compartido)
- El nombre de la persona mencionada (debtor_name) - Si el usuario menciona explícitamente a otra persona, extrae el nombre. Si no se menciona, usa null.
- La fecha de vencimiento (due_date) - Si el usuario menciona fechas relativas como "mañana", "ayer", "el próximo lunes", "en 3 días", calcula la fecha en formato YYYY-MM-DD. Si no se menciona, usa null.

IMPORTANTE: 
- Si el usuario dice "gasté", "gastamos", "pagué", "pagamos", "compré", "compramos", la acción debe ser "expense" (gasto compartido)
- Si el usuario dice "debo", "debo pagar", "tengo que pagar", "le debo", "debo dinero", la acción debe ser "debt" (deuda)
- Para "expense" (gasté): el usuario que envía el mensaje es quien pagó, y la persona mencionada es quien debe
- Para "debt" (debo): el usuario que envía el mensaje es quien debe, y la persona mencionada es quien va a recibir el pago
- Para fechas relativas, calcula la fecha basándote en la fecha actual (hoy)
- Debes devolver SOLO un JSON válido, sin texto adicional, sin markdown, sin explicaciones.

El JSON debe tener exactamente esta estructura:
{
    "amount": <número>,
    "currency": "<código de moneda>",
    "description": "<descripción>",
    "category": "<categoría>",
    "action": "<debt|expense>",
    "debtor_name": "<nombre de la persona mencionada o null si no se especifica>",
    "due_date": "<fecha en formato YYYY-MM-DD o null si no se especifica>"
}

Ejemplos:
- "Gasté 50000 con María en el supermercado" -> action: "expense", currency: "COP", debtor_name: "María", due_date: null
- "Gastamos 30000 en el taxi" -> action: "expense", currency: "COP", debtor_name: null, due_date: null
- "Le debo 30000 a María por el taxi" -> action: "debt", currency: "COP", debtor_name: "María", due_date: null
- "Debo 100000 pesos a Juan mañana" -> action: "debt", currency: "COP", debtor_name: "Juan", due_date: "2024-01-16" (si hoy es 2024-01-15)
- "Tengo que pagar 50 USD el próximo lunes" -> action: "debt", currency: "USD", debtor_name: null, due_date: "2024-01-22" (calcula el próximo lunes)
- "Debo 20 dólares ayer" -> action: "debt", currency: "USD", debtor_name: null, due_date: "2024-01-14" (si hoy es 2024-01-15)
"""

        # Prompt completo
        full_prompt = f"{system_prompt}\n\nTexto del usuario: {text}\n\nJSON:"
        
        # Preparar payload para la API de Gemini
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 1024
            }
        }
        
        # Headers con la API key
        headers = {
            "Content-Type": "application/json"
        }
        
        # Construir URL completa con API key como parámetro
        url_with_key = f"{GEMINI_API_URL}{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        # Hacer la llamada HTTP a Gemini
        log_operation(logger, "GEMINI_API_CALL",
                     f"Llamando a Gemini API: {GEMINI_API_URL}, modelo={GEMINI_MODEL}, texto_length={len(text)}",
                     error_code=ErrorCodes.OP_SUCCESS)
        
        response = requests.post(
            url_with_key,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Verificar que la respuesta sea exitosa
        response.raise_for_status()
        
        log_operation(logger, "GEMINI_API_RESPONSE",
                     f"Respuesta recibida de Gemini API: status={response.status_code}",
                     error_code=ErrorCodes.OP_SUCCESS)
        
        # Parsear respuesta JSON
        response_data = response.json()
        
        # Extraer el texto de la respuesta
        response_text = None
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            if 'content' in response_data['candidates'][0]:
                if 'parts' in response_data['candidates'][0]['content']:
                    response_text = response_data['candidates'][0]['content']['parts'][0].get('text', '').strip()
                else:
                    log_error(logger, ErrorCodes.ERR_GEMINI_API,
                             "No se encontró 'parts' en la respuesta de Gemini",
                             data_dict={"response_structure": list(response_data.get('candidates', [{}])[0].keys()) if response_data.get('candidates') else None})
                    return None
            else:
                log_error(logger, ErrorCodes.ERR_GEMINI_API,
                         "No se encontró 'content' en la respuesta de Gemini",
                         data_dict={"response_structure": list(response_data.get('candidates', [{}])[0].keys()) if response_data.get('candidates') else None})
                return None
        else:
            log_error(logger, ErrorCodes.ERR_GEMINI_API,
                     "No se encontró 'candidates' en la respuesta de Gemini",
                     data_dict={"response_data": response_data})
            return None
        
        if not response_text:
            log_error(logger, ErrorCodes.ERR_GEMINI_API,
                     "La respuesta de Gemini está vacía",
                     data_dict={"response_data": response_data})
            return None
        
        # Limpiar el texto si viene con markdown
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        # Parsear JSON
        expense_data = json.loads(response_text)
        
        # Validar campos requeridos
        required_fields = ['amount', 'currency', 'description', 'action']
        for field in required_fields:
            if field not in expense_data:
                log_error(logger, ErrorCodes.ERR_MISSING_REQUIRED_FIELD,
                         f"Campo requerido '{field}' no encontrado en la respuesta de Gemini",
                         data_dict={"expense_data": expense_data, "missing_field": field})
                return None
        
        # Asegurar que debtor_name exista (puede ser null)
        if 'debtor_name' not in expense_data:
            expense_data['debtor_name'] = None
        
        # Asegurar que due_date exista (puede ser null)
        if 'due_date' not in expense_data:
            expense_data['due_date'] = None
        
        # Validar valores
        if not isinstance(expense_data['amount'], (int, float)) or expense_data['amount'] <= 0:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                     f"Monto inválido: {expense_data['amount']}",
                     data_dict={"expense_data": expense_data})
            return None
        
        if expense_data['action'] not in ['debt', 'expense']:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                     f"Acción desconocida '{expense_data['action']}', usando 'debt' por defecto",
                     data_dict={"expense_data": expense_data})
            expense_data['action'] = 'debt'
        
        # Asegurar que currency tenga un valor por defecto (COP)
        if not expense_data.get('currency'):
            expense_data['currency'] = 'COP'
        
        log_operation(logger, "GEMINI_EXTRACTION_SUCCESS",
                     f"Datos extraídos exitosamente: amount={expense_data['amount']}, currency={expense_data['currency']}, action={expense_data['action']}",
                     error_code=ErrorCodes.OP_SUCCESS)
        return expense_data
        
    except requests.exceptions.HTTPError as e:
        error_response_text = e.response.text if hasattr(e.response, 'text') else 'N/A'
        log_error(logger, ErrorCodes.ERR_GEMINI_API,
                 f"Error HTTP al comunicarse con Gemini: {str(e)}",
                 data_dict={"status_code": e.response.status_code if hasattr(e.response, 'status_code') else None,
                           "response_text": error_response_text},
                 exception=e)
        return None
    except requests.exceptions.RequestException as e:
        log_error(logger, ErrorCodes.ERR_GEMINI_API,
                 f"Error de conexión con Gemini: {str(e)}",
                 exception=e)
        return None
    except json.JSONDecodeError as e:
        log_error(logger, ErrorCodes.ERR_GEMINI_API,
                 f"Error al parsear JSON de Gemini: {str(e)}",
                 data_dict={"response_text": response_text if 'response_text' in locals() else 'N/A'},
                 exception=e)
        return None
    except Exception as e:
        log_error(logger, ErrorCodes.ERR_GEMINI_API,
                 f"Error inesperado al comunicarse con Gemini: {str(e)}",
                 exception=e)
        return None

