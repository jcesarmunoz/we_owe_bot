"""
Configuración de logging mejorada para el proyecto
Proporciona logs estructurados con fecha, códigos de error y contexto
"""
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """
    Formatter personalizado que incluye fecha, código de error y contexto
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Obtener información básica
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        
        # Código de error (si está disponible en extra)
        error_code = getattr(record, 'error_code', 'N/A')
        direction = getattr(record, 'direction', 'INTERNAL')
        user_id = getattr(record, 'user_id', None)
        telegram_id = getattr(record, 'telegram_id', None)
        
        # Construir mensaje estructurado
        log_parts = [
            f"[{timestamp}]",
            f"[{level}]",
            f"[{logger_name}]",
            f"[DIR:{direction}]",
            f"[CODE:{error_code}]"
        ]
        
        # Agregar información de usuario si está disponible
        if user_id:
            log_parts.append(f"[USER_ID:{user_id}]")
        if telegram_id:
            log_parts.append(f"[TELEGRAM_ID:{telegram_id}]")
        
        # Agregar el mensaje
        log_parts.append(f"| {message}")
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_parts.append(f"| Exception: {self.formatException(record.exc_info)}")
        
        return " ".join(log_parts)


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    Configura el sistema de logging del proyecto
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta opcional para archivo de log
    """
    # Crear logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Formatter personalizado
    formatter = StructuredFormatter()
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def log_request(logger: logging.Logger, direction: str, endpoint: str, 
                telegram_id: Optional[int] = None, user_id: Optional[int] = None,
                data_dict: Optional[Dict[str, Any]] = None, error_code: str = 'REQ_IN'):
    """
    Log estructurado para requests entrantes
    
    Args:
        logger: Logger instance
        direction: IN (entrada) o OUT (salida)
        endpoint: Endpoint o acción
        telegram_id: ID de Telegram del usuario
        user_id: ID interno del usuario
        data_dict: Datos adicionales del request
        error_code: Código de error/operación
    """
    extra = {
        'direction': direction,
        'error_code': error_code,
        'telegram_id': telegram_id,
        'user_id': user_id
    }
    
    data_str = f" | Data: {data_dict}" if data_dict else ""
    logger.info(f"REQUEST {direction} | Endpoint: {endpoint}{data_str}", extra=extra)


def log_response(logger: logging.Logger, direction: str, endpoint: str,
                status_code: int, telegram_id: Optional[int] = None,
                user_id: Optional[int] = None, message: Optional[str] = None,
                error_code: str = 'RESP_OUT'):
    """
    Log estructurado para responses salientes
    
    Args:
        logger: Logger instance
        direction: IN o OUT
        endpoint: Endpoint o acción
        status_code: Código de estado HTTP
        telegram_id: ID de Telegram del usuario
        user_id: ID interno del usuario
        message: Mensaje adicional
        error_code: Código de error/operación
    """
    extra = {
        'direction': direction,
        'error_code': error_code,
        'telegram_id': telegram_id,
        'user_id': user_id
    }
    
    message_str = f" | Message: {message}" if message else ""
    logger.info(f"RESPONSE {direction} | Endpoint: {endpoint} | Status: {status_code}{message_str}", extra=extra)


def log_error(logger: logging.Logger, error_code: str, message: str,
              telegram_id: Optional[int] = None, user_id: Optional[int] = None,
              exception: Optional[Exception] = None, data_dict: Optional[Dict[str, Any]] = None):
    """
    Log estructurado para errores
    
    Args:
        logger: Logger instance
        error_code: Código de error único
        message: Mensaje de error
        telegram_id: ID de Telegram del usuario
        user_id: ID interno del usuario
        exception: Excepción capturada (opcional)
        data_dict: Datos adicionales del error (opcional)
    """
    extra = {
        'direction': 'ERROR',
        'error_code': error_code,
        'telegram_id': telegram_id,
        'user_id': user_id
    }
    
    data_str = f" | Data: {data_dict}" if data_dict else ""
    error_msg = f"ERROR | Code: {error_code} | {message}{data_str}"
    
    if exception:
        logger.error(error_msg, extra=extra, exc_info=True)
    else:
        logger.error(error_msg, extra=extra)


def log_operation(logger: logging.Logger, operation: str, details: str,
                  telegram_id: Optional[int] = None, user_id: Optional[int] = None,
                  error_code: str = 'OP_SUCCESS'):
    """
    Log estructurado para operaciones del sistema
    
    Args:
        logger: Logger instance
        operation: Nombre de la operación
        details: Detalles de la operación
        telegram_id: ID de Telegram del usuario
        user_id: ID interno del usuario
        error_code: Código de operación
    """
    extra = {
        'direction': 'OPERATION',
        'error_code': error_code,
        'telegram_id': telegram_id,
        'user_id': user_id
    }
    
    logger.info(f"OPERATION | {operation} | {details}", extra=extra)


# Códigos de error del sistema
class ErrorCodes:
    """Códigos de error estandarizados del sistema"""
    # Requests
    REQ_IN = 'REQ_IN'
    REQ_OUT = 'REQ_OUT'
    
    # Responses
    RESP_OK = 'RESP_OK'
    RESP_ERROR = 'RESP_ERROR'
    RESP_NOT_FOUND = 'RESP_NOT_FOUND'
    RESP_UNAUTHORIZED = 'RESP_UNAUTHORIZED'
    
    # Operaciones
    OP_SUCCESS = 'OP_SUCCESS'
    OP_FAILED = 'OP_FAILED'
    
    # Errores específicos
    ERR_DB_CONNECTION = 'ERR_DB_001'
    ERR_DB_QUERY = 'ERR_DB_002'
    ERR_TELEGRAM_API = 'ERR_TG_001'
    ERR_GEMINI_API = 'ERR_GM_001'
    ERR_USER_NOT_FOUND = 'ERR_USR_001'
    ERR_USER_NOT_AUTHORIZED = 'ERR_USR_002'
    ERR_EXPENSE_CREATION = 'ERR_EXP_001'
    ERR_EXPENSE_NOT_FOUND = 'ERR_EXP_002'
    ERR_INVALID_DATA = 'ERR_VAL_001'
    ERR_MISSING_REQUIRED_FIELD = 'ERR_VAL_002'
    ERR_NO_OTHER_USER = 'ERR_USR_003'

