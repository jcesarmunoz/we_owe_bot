"""
Rutas de la aplicación Flask
"""
import logging
from typing import Optional
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Expense
from app.bot_services import (
    send_message,
    is_user_authorized,
    create_user,
    create_expense,
    format_expense_confirmation,
    format_payment_receipt,
    get_user_by_telegram_id,
    get_user_expenses,
    format_expenses_summary,
    get_user_debts_to_pay,
    get_user_debts_to_collect,
    format_debts_list_for_payment,
    format_debts_to_collect,
    mark_expense_as_paid,
    answer_callback_query,
    edit_message_text
)
from app.ai_services import extract_expense_data
from app.logger_config import (
    log_request, log_response, log_error, log_operation, ErrorCodes
)

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


def get_telegram_id_from_update(update: dict) -> Optional[int]:
    """
    Extrae el telegram_id del update de Telegram

    Args:
        update: Diccionario con el update de Telegram
.
    Returns:
        telegram_id del usuario o None si no se encuentra
    """
    if 'message' in update:
        return update['message']['from']['id']
    elif 'callback_query' in update:
        return update['callback_query']['from']['id']
    return None


def get_message_text_from_update(update: dict) -> Optional[str]:
    """
    Extrae el texto del mensaje del update de Telegram

    Args:
        update: Diccionario con el update de Telegram

    Returns:
        Texto del mensaje o None
    """
    if 'message' in update and 'text' in update['message']:
        return update['message']['text']
    return None


@bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal para recibir updates de Telegram

    Flujo:
    1. Recibe el update de Telegram
    2. Verifica autorización del usuario
    3. Procesa el mensaje con Gemini
    4. Guarda el gasto en la base de datos
    5. Envía confirmación al usuario
    """
    try:
        update = request.get_json()
        
        log_request(logger, "IN", "/webhook", data_dict={"has_update": update is not None})

        if not update:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA, "Update vacío recibido")
            log_response(logger, "OUT", "/webhook", 400, error_code=ErrorCodes.RESP_ERROR)
            return jsonify({'status': 'error', 'message': 'Empty update'}), 400

        # Manejar callback queries (botones inline) primero - DEBE ser lo primero
        # Esto previene que los clicks en botones se procesen como mensajes de texto
        if 'callback_query' in update:
            callback_data = update.get('callback_query', {}).get('data', '')
            telegram_id_callback = update.get('callback_query', {}).get('from', {}).get('id')
            log_operation(logger, "CALLBACK_QUERY_RECEIVED",
                         f"Callback query recibido: data={callback_data[:50]}, telegram_id={telegram_id_callback}",
                         telegram_id=telegram_id_callback)
            result = handle_callback_query(update)
            log_response(logger, "OUT", "/webhook", 200, 
                        telegram_id=telegram_id_callback,
                        message="Callback query procesado exitosamente", 
                        error_code=ErrorCodes.RESP_OK)
            return result

        # Obtener telegram_id y texto del mensaje (solo si NO es callback_query)
        telegram_id = get_telegram_id_from_update(update)
        message_text = get_message_text_from_update(update)

        if not telegram_id:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA, 
                      "No se pudo obtener telegram_id del update",
                      data_dict={"update_keys": list(update.keys()) if update else None})
            log_response(logger, "OUT", "/webhook", 200, telegram_id=telegram_id)
            return jsonify({'status': 'ok'}), 200

        # Manejar comandos especiales
        if message_text:
            message_lower = message_text.lower().strip()
            
            if message_text.startswith('/start'):
                return handle_start_command(telegram_id, update)
            elif message_text.startswith('/admin'):
                return handle_admin_command(telegram_id, message_text)
            elif any(keyword in message_lower for keyword in [
                'ver mis gastos', 'lista de deudas', 'lista de gastos',
                'mis gastos', 'ver gastos', 'mostrar gastos',
                'gastos pendientes', 'deudas pendientes', 'resumen'
            ]):
                # Verificar autorización antes de mostrar gastos
                authorized, user = is_user_authorized(telegram_id)
                if not authorized:
                    if user:
                        send_message(
                            telegram_id, "❌ No estás autorizado para usar este bot.")
                    else:
                        send_message(
                            telegram_id,
                            "❌ No estás registrado. Usa /start para registrarte."
                        )
                    return jsonify({'status': 'ok'}), 200
                
                if not user:
                    logger.error("Usuario autorizado pero user es None")
                    return jsonify({'status': 'error', 'message': 'Internal error'}), 500
                
                return handle_list_expenses(telegram_id, user)
            elif any(keyword in message_lower for keyword in [
                'pagar', 'pagar deuda', 'pagar deudas', 'quiero pagar',
                'pago', 'realizar pago', 'mis deudas'
            ]):
                # Verificar autorización antes de mostrar deudas para pagar
                authorized, user = is_user_authorized(telegram_id)
                if not authorized:
                    if user:
                        send_message(
                            telegram_id, "❌ No estás autorizado para usar este bot.")
                    else:
                        send_message(
                            telegram_id,
                            "❌ No estás registrado. Usa /start para registrarte."
                        )
                    return jsonify({'status': 'ok'}), 200
                
                if not user:
                    logger.error("Usuario autorizado pero user es None")
                    return jsonify({'status': 'error', 'message': 'Internal error'}), 500
                
                return handle_pay_debts(telegram_id, user)
            elif any(keyword in message_lower for keyword in [
                'quien me debe', 'quién me debe', 'cobrar', 'debo cobrar',
                'me deben', 'quien me debe dinero', 'quién me debe dinero'
            ]):
                # Verificar autorización antes de mostrar deudas a cobrar
                authorized, user = is_user_authorized(telegram_id)
                if not authorized:
                    if user:
                        send_message(
                            telegram_id, "❌ No estás autorizado para usar este bot.")
                    else:
                        send_message(
                            telegram_id,
                            "❌ No estás registrado. Usa /start para registrarte."
                        )
                    return jsonify({'status': 'ok'}), 200
                
                if not user:
                    logger.error("Usuario autorizado pero user es None")
                    return jsonify({'status': 'error', 'message': 'Internal error'}), 500
                
                return handle_collect_debts(telegram_id, user)

        # Verificar autorización
        authorized, user = is_user_authorized(telegram_id)

        if not authorized:
            if user:
                send_message(
                    telegram_id, "❌ No estás autorizado para usar este bot.")
            else:
                send_message(
                    telegram_id,
                    "❌ No estás registrado. Usa /start para registrarte."
                )
            return jsonify({'status': 'ok'}), 200

        # En este punto, si authorized es True, user no puede ser None
        if not user:
            logger.error("Usuario autorizado pero user es None")
            return jsonify({'status': 'error', 'message': 'Internal error'}), 500

        # Si no hay mensaje de texto, ignorar
        if not message_text:
            return jsonify({'status': 'ok'}), 200

        # Extraer datos con Gemini
        log_operation(logger, "GEMINI_EXTRACTION", f"Extrayendo datos del mensaje: {message_text[:50]}...",
                     telegram_id=telegram_id, user_id=user.id)
        expense_data = extract_expense_data(message_text)

        if not expense_data:
            log_error(logger, ErrorCodes.ERR_GEMINI_API,
                     "No se pudieron extraer datos del mensaje con Gemini",
                     telegram_id=telegram_id, user_id=user.id)
            send_message(
                telegram_id,
                "❌ No pude procesar tu mensaje. Por favor, intenta de nuevo con un formato claro.\n\n"
                "Ejemplo: 'Gasté 50000 en el supermercado'"
            )
            log_response(logger, "OUT", "/webhook", 200, telegram_id=telegram_id, user_id=user.id)
            return jsonify({'status': 'ok'}), 200

        # Determinar payer_id y debtor_id basándose en la acción
        action = expense_data.get('action', 'debt')
        mentioned_name = expense_data.get('debtor_name')  # Nombre de la persona mencionada
        
        # REGLA 1: Si dice "gasté" (action == "expense"):
        #   - Quien envía el mensaje es el cobrador (payer)
        #   - La persona mencionada es el deudor (debtor)
        # REGLA 2: Si dice "debo" (action == "debt"):
        #   - Quien envía el mensaje es el deudor (debtor)
        #   - La persona mencionada es el cobrador (payer)
        
        if action == 'expense':
            # Caso "gasté": el usuario es quien pagó (cobrador)
            payer_id = user.id
            debtor_id = None
            
            # Buscar quién debe (debtor) basándose en el nombre mencionado
            if mentioned_name:
                # Buscar usuario por nombre (búsqueda flexible, case-insensitive)
                debtor_user = User.query.filter(
                    db.func.lower(User.name).like(f"%{mentioned_name.lower()}%")
                ).filter(User.id != user.id).first()
                
                if debtor_user:
                    debtor_id = debtor_user.id
                    log_operation(logger, "USER_SEARCH", 
                                f"Usuario deudor encontrado por nombre '{mentioned_name}': {debtor_user.name}",
                                telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)
                else:
                    # Si no se encuentra, listar usuarios disponibles
                    all_users = User.query.filter(User.id != user.id).all()
                    if all_users:
                        user_list = ", ".join([u.name for u in all_users])
                        send_message(
                            telegram_id,
                            f"❌ No encontré un usuario llamado '{mentioned_name}'.\n\n"
                            f"Usuarios disponibles: {user_list}\n\n"
                            f"Por favor, verifica el nombre e intenta de nuevo.\n"
                            f"Ejemplo: 'Gasté 50000 con {all_users[0].name} en el supermercado'"
                        )
                        log_error(logger, ErrorCodes.ERR_USER_NOT_FOUND,
                                 f"Usuario '{mentioned_name}' no encontrado. Usuarios disponibles: {user_list}",
                                 telegram_id=telegram_id, user_id=user.id)
                    else:
                        send_message(
                            telegram_id,
                            "⚠️ Solo hay un usuario registrado. Necesitas registrar otro usuario primero."
                        )
                        log_error(logger, ErrorCodes.ERR_USER_NOT_FOUND,
                                 f"Usuario '{mentioned_name}' no encontrado y solo hay un usuario registrado",
                                 telegram_id=telegram_id, user_id=user.id)
                    return jsonify({'status': 'ok'}), 200
            else:
                # Si no se menciona a nadie en "gasté", no se puede determinar el deudor
                send_message(
                    telegram_id,
                    "❌ Para registrar un gasto compartido, debes mencionar con quién gastaste.\n\n"
                    "Ejemplo: 'Gasté 50000 con María en el supermercado'"
                )
                log_error(logger, ErrorCodes.ERR_NO_OTHER_USER,
                         "Gasto compartido sin mencionar a otra persona",
                         telegram_id=telegram_id, user_id=user.id)
                return jsonify({'status': 'ok'}), 200
        else:
            # Caso "debo": el usuario es quien debe (deudor)
            debtor_id = user.id
            payer_id = None
            
            # Buscar quién va a recibir el pago (payer) basándose en el nombre mencionado
            if mentioned_name:
                # Buscar usuario por nombre (búsqueda flexible, case-insensitive)
                payer_user = User.query.filter(
                    db.func.lower(User.name).like(f"%{mentioned_name.lower()}%")
                ).filter(User.id != user.id).first()
                
                if payer_user:
                    payer_id = payer_user.id
                    log_operation(logger, "USER_SEARCH", 
                                f"Usuario pagador encontrado por nombre '{mentioned_name}': {payer_user.name}",
                                telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)
                else:
                    # Si no se encuentra, listar usuarios disponibles
                    all_users = User.query.filter(User.id != user.id).all()
                    if all_users:
                        user_list = ", ".join([u.name for u in all_users])
                        send_message(
                            telegram_id,
                            f"❌ No encontré un usuario llamado '{mentioned_name}'.\n\n"
                            f"Usuarios disponibles: {user_list}\n\n"
                            f"Por favor, verifica el nombre e intenta de nuevo.\n"
                            f"Ejemplo: 'Le debo 50000 a {all_users[0].name}'"
                        )
                        log_error(logger, ErrorCodes.ERR_USER_NOT_FOUND,
                                 f"Usuario '{mentioned_name}' no encontrado. Usuarios disponibles: {user_list}",
                                 telegram_id=telegram_id, user_id=user.id)
                    else:
                        send_message(
                            telegram_id,
                            "⚠️ Solo hay un usuario registrado. Necesitas registrar otro usuario primero."
                        )
                        log_error(logger, ErrorCodes.ERR_USER_NOT_FOUND,
                                 f"Usuario '{mentioned_name}' no encontrado y solo hay un usuario registrado",
                                 telegram_id=telegram_id, user_id=user.id)
                    return jsonify({'status': 'ok'}), 200
            else:
                # Si no se especifica nombre, usar la lógica por defecto
                # Buscar el otro usuario (asumiendo solo 2 usuarios)
                other_user = User.query.filter(User.id != user.id).first()
                
                if not other_user:
                    send_message(
                        telegram_id,
                        "⚠️ Solo hay un usuario registrado. Necesitas registrar otro usuario primero.\n\n"
                        "💡 Tip: Puedes especificar a quién le debes en tu mensaje.\n"
                        "Ejemplo: 'Le debo 50000 a María'"
                    )
                    log_error(logger, ErrorCodes.ERR_USER_NOT_FOUND,
                              "Solo hay un usuario registrado. No se puede determinar el pagador.",
                              telegram_id=telegram_id, user_id=user.id)
                    return jsonify({'status': 'ok'}), 200
                
                payer_id = other_user.id
                log_operation(logger, "DEFAULT_PAYER",
                             f"No se especificó nombre de pagador, usando usuario por defecto: {other_user.name}",
                             telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)
        
        # Validar que tenemos ambos IDs
        if not payer_id or not debtor_id:
            log_error(logger, ErrorCodes.ERR_EXPENSE_CREATION,
                     f"No se pudo determinar payer_id o debtor_id. payer_id={payer_id}, debtor_id={debtor_id}",
                     telegram_id=telegram_id, user_id=user.id)
            send_message(
                telegram_id,
                "❌ Error al procesar el gasto. No se pudo determinar quién pagó o quién debe."
            )
            return jsonify({'status': 'error', 'message': 'Could not determine payer or debtor'}), 500

        # Si la acción es "expense", ambos comparten el gasto (50/50)
        # Por ahora, lo tratamos igual que una deuda

        # Crear el gasto
        log_operation(logger, "EXPENSE_CREATION",
                     f"Creando gasto: payer_id={payer_id}, debtor_id={debtor_id}, amount={expense_data['amount']}, currency={expense_data['currency']}",
                     telegram_id=telegram_id, user_id=user.id)
        expense = create_expense(
            payer_id=payer_id,
            debtor_id=debtor_id,
            amount=float(expense_data['amount']),
            currency=expense_data['currency'],
            description=expense_data['description'],
            raw_text=message_text,
            category=expense_data.get('category'),
            due_date=expense_data.get('due_date')
        )

        log_operation(logger, "EXPENSE_CREATED",
                     f"Gasto creado exitosamente: expense_id={expense.id}",
                     telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)

        # Enviar confirmación
        confirmation_message = format_expense_confirmation(expense)
        send_message(telegram_id, confirmation_message)

        log_response(logger, "OUT", "/webhook", 200, telegram_id=telegram_id, user_id=user.id,
                    message="Gasto creado exitosamente", error_code=ErrorCodes.RESP_OK)
        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        user_id_val = user.id if 'user' in locals() and user else None
        log_error(logger, ErrorCodes.ERR_EXPENSE_CREATION,
                 f"Error en webhook: {str(e)}",
                 telegram_id=telegram_id if 'telegram_id' in locals() else None,
                 user_id=user_id_val,
                 exception=e)
        log_response(logger, "OUT", "/webhook", 500, 
                    telegram_id=telegram_id if 'telegram_id' in locals() else None,
                    error_code=ErrorCodes.RESP_ERROR)
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_start_command(telegram_id: int, update: dict):
    """
    Maneja el comando /start para registrar nuevos usuarios

    Args:
        telegram_id: ID de Telegram del usuario
        update: Update completo de Telegram
    """
    try:
        # Obtener información del usuario desde Telegram
        if update and 'message' in update:
            from_info = update['message']['from']
            user_name = f"{from_info.get('first_name', '')} {from_info.get('last_name', '')}".strip(
            )
            if not user_name:
                user_name = from_info.get('username', 'Usuario')
        else:
            user_name = "Usuario"

        # Verificar si el usuario ya existe
        existing_user = get_user_by_telegram_id(telegram_id)

        if existing_user:
            send_message(
                telegram_id,
                f"👋 ¡Hola {existing_user.name}! Ya estás registrado.\n\n"
                "Envía un mensaje con un gasto para registrarlo.\n"
                "Ejemplo: 'Gasté 50000 en el supermercado'"
            )
        else:
            # Crear nuevo usuario
            new_user = create_user(telegram_id, user_name, is_authorized=True)
            send_message(
                telegram_id,
                f"✅ ¡Bienvenido {new_user.name}!\n\n"
                "Ya estás registrado en el bot. Puedes empezar a registrar gastos.\n\n"
                "Ejemplo: 'Gasté 50000 en el supermercado'"
            )

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"Error en handle_start_command: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_admin_command(telegram_id: int, message_text: str):
    """
    Maneja comandos de administración
    /admin add <telegram_id> <nombre> - Agrega un usuario
    /admin list - Lista todos los usuarios
    /admin authorize <telegram_id> - Autoriza un usuario
    /admin deauthorize <telegram_id> - Desautoriza un usuario

    Args:
        telegram_id: ID de Telegram del usuario que ejecuta el comando
        message_text: Texto completo del mensaje con el comando
    """
    try:

        parts = message_text.split()

        if len(parts) < 2:
            send_message(
                telegram_id,
                "❌ Uso: /admin <comando>\n\n"
                "Comandos disponibles:\n"
                "/admin add <telegram_id> <nombre>\n"
                "/admin list\n"
                "/admin authorize <telegram_id>\n"
                "/admin deauthorize <telegram_id>"
            )
            return jsonify({'status': 'ok'}), 200

        command = parts[1].lower()

        if command == 'add' and len(parts) >= 4:
            # /admin add <telegram_id> <nombre>
            try:
                new_telegram_id = int(parts[2])
                name = ' '.join(parts[3:])

                # Verificar si ya existe
                if get_user_by_telegram_id(new_telegram_id):
                    send_message(
                        telegram_id, f"❌ El usuario con telegram_id {new_telegram_id} ya existe.")
                else:
                    new_user = create_user(
                        new_telegram_id, name, is_authorized=True)
                    send_message(
                        telegram_id, f"✅ Usuario agregado: {new_user.name} (ID: {new_user.telegram_id})")
            except ValueError:
                send_message(
                    telegram_id, "❌ El telegram_id debe ser un número.")

        elif command == 'list':
            # /admin list
            users = User.query.all()
            if not users:
                send_message(telegram_id, "📋 No hay usuarios registrados.")
            else:
                message = "📋 <b>Usuarios registrados:</b>\n\n"
                for user in users:
                    status = "✅ Autorizado" if user.is_authorized else "❌ No autorizado"
                    message += f"• {user.name} (ID: {user.telegram_id}) - {status}\n"
                send_message(telegram_id, message)

        elif command == 'authorize' and len(parts) >= 3:
            # /admin authorize <telegram_id>
            try:
                target_telegram_id = int(parts[2])
                user = get_user_by_telegram_id(target_telegram_id)
                if user:
                    user.is_authorized = True
                    db.session.commit()
                    send_message(
                        telegram_id, f"✅ Usuario {user.name} autorizado.")
                else:
                    send_message(
                        telegram_id, f"❌ Usuario con telegram_id {target_telegram_id} no encontrado.")
            except ValueError:
                send_message(
                    telegram_id, "❌ El telegram_id debe ser un número.")

        elif command == 'deauthorize' and len(parts) >= 3:
            # /admin deauthorize <telegram_id>
            try:
                target_telegram_id = int(parts[2])
                user = get_user_by_telegram_id(target_telegram_id)
                if user:
                    user.is_authorized = False
                    db.session.commit()
                    send_message(
                        telegram_id, f"❌ Usuario {user.name} desautorizado.")
                else:
                    send_message(
                        telegram_id, f"❌ Usuario con telegram_id {target_telegram_id} no encontrado.")
            except ValueError:
                send_message(
                    telegram_id, "❌ El telegram_id debe ser un número.")

        else:
            send_message(
                telegram_id, "❌ Comando no reconocido. Usa /admin list para ver ayuda.")

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"Error en handle_admin_command: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_list_expenses(telegram_id: int, user: User):
    """
    Maneja la solicitud de ver la lista de gastos del usuario
    
    Args:
        telegram_id: ID de Telegram del usuario
        user: Objeto User
    """
    try:
        # Obtener gastos del usuario
        expenses_to_pay, expenses_to_collect = get_user_expenses(user.id)
        
        # Formatear y enviar el resumen
        summary_message = format_expenses_summary(user, expenses_to_pay, expenses_to_collect)
        send_message(telegram_id, summary_message)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error en handle_list_expenses: {e}", exc_info=True)
        send_message(
            telegram_id,
            "❌ Error al obtener tus gastos. Por favor, intenta de nuevo más tarde."
        )
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_pay_debts(telegram_id: int, user: User):
    """
    Maneja la solicitud de pagar deudas - muestra lista numerada con botones
    
    Args:
        telegram_id: ID de Telegram del usuario
        user: Objeto User
    """
    try:
        # Obtener solo las deudas que el usuario debe pagar
        debts = get_user_debts_to_pay(user.id)
        
        # Formatear mensaje con botones inline
        message, reply_markup = format_debts_list_for_payment(debts)
        send_message(telegram_id, message, reply_markup)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error en handle_pay_debts: {e}", exc_info=True)
        send_message(
            telegram_id,
            "❌ Error al obtener tus deudas. Por favor, intenta de nuevo más tarde."
        )
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_collect_debts(telegram_id: int, user: User):
    """
    Maneja la solicitud de ver quién le debe - muestra lista de deudas a cobrar
    
    Args:
        telegram_id: ID de Telegram del usuario
        user: Objeto User
    """
    try:
        # Obtener solo las deudas que el usuario debe cobrar (donde es pagador)
        debts_to_collect = get_user_debts_to_collect(user.id)
        
        if not debts_to_collect:
            send_message(telegram_id, "✅ No tienes deudas pendientes por cobrar.")
            return jsonify({'status': 'ok'}), 200
        
        # Formatear mensaje con la lista de deudas a cobrar
        message = format_debts_to_collect(debts_to_collect)
        send_message(telegram_id, message)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error en handle_collect_debts: {e}", exc_info=True)
        send_message(
            telegram_id,
            "❌ Error al obtener tus deudas por cobrar. Por favor, intenta de nuevo más tarde."
        )
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_callback_query(update: dict):
    """
    Maneja los callback queries (clicks en botones inline)
    
    Args:
        update: Update de Telegram con callback_query
    """
    try:
        callback_query = update.get('callback_query', {})
        callback_data = callback_query.get('data', '')
        callback_query_id = callback_query.get('id', '')
        telegram_id = callback_query.get('from', {}).get('id')
        message = callback_query.get('message', {})
        message_id = message.get('message_id')
        chat_id = message.get('chat', {}).get('id')
        
        if not telegram_id:
            logger.warning("No se pudo obtener telegram_id del callback_query")
            return jsonify({'status': 'ok'}), 200
        
        # Verificar autorización
        authorized, user = is_user_authorized(telegram_id)
        if not authorized:
            answer_callback_query(callback_query_id, "❌ No estás autorizado.", show_alert=True)
            return jsonify({'status': 'ok'}), 200
        
        if not user:
            answer_callback_query(callback_query_id, "❌ Error interno.", show_alert=True)
            return jsonify({'status': 'ok'}), 200
        
        # Manejar diferentes tipos de callbacks
        if not callback_data:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                     "Callback query sin data recibido",
                     telegram_id=telegram_id)
            answer_callback_query(callback_query_id, "❌ Error: callback sin datos.", show_alert=True)
            return jsonify({'status': 'ok'}), 200
        
        if callback_data.startswith('pay_debt_'):
            # Extraer ID de la deuda
            try:
                debt_id = int(callback_data.replace('pay_debt_', ''))
                log_operation(logger, "DEBT_PAYMENT_INITIATED",
                             f"Iniciando pago de deuda: debt_id={debt_id}",
                             telegram_id=telegram_id, user_id=user.id)
            except ValueError:
                log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                         f"ID de deuda inválido en callback: {callback_data}",
                         telegram_id=telegram_id, user_id=user.id)
                answer_callback_query(callback_query_id, "❌ ID de deuda inválido.", show_alert=True)
                return jsonify({'status': 'ok'}), 200
            
            # Verificar que la deuda pertenece al usuario
            expense = Expense.query.get(debt_id)
            if not expense:
                log_error(logger, ErrorCodes.ERR_EXPENSE_NOT_FOUND,
                         f"Deuda no encontrada: debt_id={debt_id}",
                         telegram_id=telegram_id, user_id=user.id)
                answer_callback_query(callback_query_id, "❌ Deuda no encontrada.", show_alert=True)
                return jsonify({'status': 'ok'}), 200
            
            if expense.debtor_id != user.id:
                log_error(logger, ErrorCodes.ERR_USER_NOT_AUTHORIZED,
                         f"Usuario intentando pagar deuda que no le pertenece: debt_id={debt_id}, user_id={user.id}, debtor_id={expense.debtor_id}",
                         telegram_id=telegram_id, user_id=user.id)
                answer_callback_query(callback_query_id, "❌ Esta deuda no te pertenece.", show_alert=True)
                return jsonify({'status': 'ok'}), 200
            
            if expense.is_settled:
                log_operation(logger, "DEBT_ALREADY_PAID",
                             f"Intento de pagar deuda ya pagada: debt_id={debt_id}",
                             telegram_id=telegram_id, user_id=user.id)
                answer_callback_query(callback_query_id, "✅ Esta deuda ya está pagada.", show_alert=True)
                return jsonify({'status': 'ok'}), 200
            
            # Marcar como pagada
            updated_expense = mark_expense_as_paid(debt_id)
            if updated_expense:
                # Responder al callback primero
                answer_callback_query(callback_query_id, f"✅ Deuda pagada: {updated_expense.amount} {updated_expense.currency}")
                
                log_operation(logger, "DEBT_PAYMENT_SUCCESS",
                             f"Deuda pagada exitosamente: debt_id={debt_id}, amount={updated_expense.amount} {updated_expense.currency}",
                             telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)
                
                # Enviar comprobante de pago como mensaje nuevo
                receipt_message = format_payment_receipt(updated_expense)
                send_message(chat_id, receipt_message)
                
                # Obtener deudas restantes y actualizar el mensaje original
                remaining_debts = get_user_debts_to_pay(user.id)
                
                if remaining_debts:
                    # Calcular totales por moneda
                    from collections import defaultdict
                    totals_by_currency = defaultdict(float)
                    for debt in remaining_debts:
                        totals_by_currency[debt.currency] += float(debt.amount)
                    
                    # Crear mensaje con resumen y lista de deudas restantes
                    remaining_message = (
                        f"💳 <b>Deudas Pendientes Restantes</b>\n\n"
                        f"📊 Total de deudas: {len(remaining_debts)}\n\n"
                    )
                    
                    # Agregar totales por moneda
                    if totals_by_currency:
                        remaining_message += "<b>💰 Total a pagar:</b>\n"
                        for currency, total in totals_by_currency.items():
                            remaining_message += f"• {total:,.2f} {currency}\n"
                        remaining_message += "\n"
                    
                    # Agregar lista de deudas con botones
                    debts_list, reply_markup = format_debts_list_for_payment(remaining_debts)
                    # Extraer solo la lista de deudas (sin el encabezado duplicado)
                    if "💳 <b>Deudas Pendientes - Selecciona una para pagar:</b>\n\n" in debts_list:
                        debts_only = debts_list.split("💳 <b>Deudas Pendientes - Selecciona una para pagar:</b>\n\n", 1)[1]
                        remaining_message += debts_only
                    else:
                        remaining_message += debts_list
                    
                    edit_message_text(chat_id, message_id, remaining_message, reply_markup)
                else:
                    # No quedan deudas pendientes
                    final_message = (
                        "✅ <b>¡Felicidades!</b>\n\n"
                        "🎉 No tienes más deudas pendientes.\n"
                        "Todas tus deudas han sido saldadas."
                    )
                    edit_message_text(chat_id, message_id, final_message)
            else:
                log_error(logger, ErrorCodes.ERR_EXPENSE_CREATION,
                         f"Error al marcar deuda como pagada: debt_id={debt_id}",
                         telegram_id=telegram_id, user_id=user.id)
                answer_callback_query(callback_query_id, "❌ Error al marcar la deuda como pagada.", show_alert=True)
        else:
            # Callback desconocido
            log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                     f"Tipo de callback desconocido: {callback_data}",
                     telegram_id=telegram_id, user_id=user.id)
            answer_callback_query(callback_query_id, "❌ Tipo de callback desconocido.", show_alert=True)
        
        log_response(logger, "OUT", "/webhook", 200, telegram_id=telegram_id, user_id=user.id,
                    message="Callback query procesado", error_code=ErrorCodes.RESP_OK)
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error en handle_callback_query: {e}", exc_info=True)
        if 'callback_query_id' in locals():
            answer_callback_query(callback_query_id, "❌ Error al procesar la solicitud.", show_alert=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({'status': 'ok', 'message': 'Bot is running'}), 200
