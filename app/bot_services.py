"""
Servicios del bot de Telegram
"""
import logging
from typing import Optional, Tuple
import requests
from app.config import Config
from app import db
from app.models import User, Expense
from app.logger_config import log_operation, log_error, ErrorCodes

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"


def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
    """
    Envía un mensaje a través de la API de Telegram
    
    Args:
        chat_id: ID del chat de Telegram
        text: Texto del mensaje a enviar
        reply_markup: Opcional, diccionario con botones inline (keyboard)
        
    Returns:
        True si el mensaje se envió correctamente, False en caso contrario
    """
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        log_operation(logger, "TELEGRAM_SEND_MESSAGE", 
                     f"Enviando mensaje a chat_id={chat_id}, length={len(text)}",
                     telegram_id=chat_id, error_code=ErrorCodes.OP_SUCCESS)
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        log_operation(logger, "TELEGRAM_MESSAGE_SENT",
                     f"Mensaje enviado exitosamente a chat_id={chat_id}",
                     telegram_id=chat_id, error_code=ErrorCodes.OP_SUCCESS)
        return True
    except requests.exceptions.RequestException as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error al enviar mensaje a Telegram: {str(e)}",
                 telegram_id=chat_id, exception=e)
        return False
    except Exception as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error inesperado al enviar mensaje: {str(e)}",
                 telegram_id=chat_id, exception=e)
        return False


def answer_callback_query(callback_query_id: str, text: str = "", show_alert: bool = False) -> bool:
    """
    Responde a un callback query de Telegram
    
    Args:
        callback_query_id: ID del callback query
        text: Texto de respuesta (opcional)
        show_alert: Si True, muestra una alerta en lugar de notificación
        
    Returns:
        True si se respondió correctamente, False en caso contrario
    """
    try:
        url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
        payload = {
            'callback_query_id': callback_query_id,
            'text': text,
            'show_alert': show_alert
        }
        
        log_operation(logger, "TELEGRAM_ANSWER_CALLBACK",
                     f"Respondiendo callback_query_id={callback_query_id}, text={text[:50]}",
                     error_code=ErrorCodes.OP_SUCCESS)
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        log_operation(logger, "TELEGRAM_CALLBACK_ANSWERED",
                     f"Callback query respondido exitosamente: {callback_query_id}",
                     error_code=ErrorCodes.OP_SUCCESS)
        return True
    except requests.exceptions.RequestException as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error al responder callback query: {str(e)}",
                 exception=e)
        return False
    except Exception as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error inesperado al responder callback: {str(e)}",
                 exception=e)
        return False


def edit_message_text(chat_id: int, message_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
    """
    Edita un mensaje existente en Telegram
    
    Args:
        chat_id: ID del chat
        message_id: ID del mensaje a editar
        text: Nuevo texto del mensaje
        reply_markup: Opcional, diccionario con botones inline
        
    Returns:
        True si se editó correctamente, False en caso contrario
    """
    try:
        url = f"{TELEGRAM_API_URL}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        log_operation(logger, "TELEGRAM_EDIT_MESSAGE",
                     f"Editando mensaje chat_id={chat_id}, message_id={message_id}",
                     telegram_id=chat_id, error_code=ErrorCodes.OP_SUCCESS)
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        log_operation(logger, "TELEGRAM_MESSAGE_EDITED",
                     f"Mensaje editado exitosamente: chat_id={chat_id}, message_id={message_id}",
                     telegram_id=chat_id, error_code=ErrorCodes.OP_SUCCESS)
        return True
    except requests.exceptions.RequestException as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error al editar mensaje: {str(e)}",
                 telegram_id=chat_id, exception=e)
        return False
    except Exception as e:
        log_error(logger, ErrorCodes.ERR_TELEGRAM_API,
                 f"Error inesperado al editar mensaje: {str(e)}",
                 telegram_id=chat_id, exception=e)
        return False


def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su telegram_id
    
    Args:
        telegram_id: ID de Telegram del usuario
        
    Returns:
        Objeto User si existe, None en caso contrario
    """
    return User.query.filter_by(telegram_id=telegram_id).first()


def is_user_authorized(telegram_id: int) -> Tuple[bool, Optional[User]]:
    """
    Verifica si un usuario está autorizado para usar el bot
    
    Args:
        telegram_id: ID de Telegram del usuario
        
    Returns:
        Tupla (is_authorized, user_object)
    """
    user = get_user_by_telegram_id(telegram_id)
    
    if not user:
        return False, None
    
    if not user.is_authorized:
        return False, user
    
    return True, user


def create_user(telegram_id: int, name: str, is_authorized: bool = True) -> User:
    """
    Crea un nuevo usuario en la base de datos
    
    Args:
        telegram_id: ID de Telegram del usuario
        name: Nombre del usuario
        is_authorized: Si el usuario está autorizado por defecto
        
    Returns:
        Objeto User creado
    """
    log_operation(logger, "USER_CREATION",
                 f"Creando usuario: telegram_id={telegram_id}, name={name}, is_authorized={is_authorized}",
                 telegram_id=telegram_id, error_code=ErrorCodes.OP_SUCCESS)
    
    user = User(
        telegram_id=telegram_id,
        name=name,
        is_authorized=is_authorized
    )
    db.session.add(user)
    db.session.commit()
    
    log_operation(logger, "USER_CREATED",
                 f"Usuario creado exitosamente: user_id={user.id}, name={user.name}",
                 telegram_id=telegram_id, user_id=user.id, error_code=ErrorCodes.OP_SUCCESS)
    return user


def create_expense(
    payer_id: int,
    debtor_id: int,
    amount: float,
    currency: str,
    description: str,
    raw_text: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[str] = None
) -> Expense:
    """
    Crea un nuevo gasto en la base de datos
    
    Args:
        payer_id: ID del usuario que pagó
        debtor_id: ID del usuario que debe
        amount: Monto del gasto
        currency: Moneda del gasto
        description: Descripción del gasto
        raw_text: Texto original del mensaje
        category: Categoría del gasto
        due_date: Fecha de vencimiento en formato YYYY-MM-DD o None
        
    Returns:
        Objeto Expense creado
    """
    from datetime import datetime
    
    log_operation(logger, "EXPENSE_CREATION_DB",
                 f"Creando gasto en DB: payer_id={payer_id}, debtor_id={debtor_id}, amount={amount}, currency={currency}, due_date={due_date}",
                 error_code=ErrorCodes.OP_SUCCESS)
    
    # Convertir due_date de string a date si se proporciona
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
            log_operation(logger, "DATE_PARSED",
                         f"Fecha parseada correctamente: {due_date} -> {due_date_obj}",
                         error_code=ErrorCodes.OP_SUCCESS)
        except ValueError:
            log_error(logger, ErrorCodes.ERR_INVALID_DATA,
                     f"Formato de fecha inválido: {due_date}",
                     exception=None)
            due_date_obj = None
    
    expense = Expense(
        payer_id=payer_id,
        debtor_id=debtor_id,
        amount=amount,
        currency=currency,
        description=description,
        raw_text=raw_text,
        category=category,
        due_date=due_date_obj
    )
    db.session.add(expense)
    db.session.commit()
    
    log_operation(logger, "EXPENSE_CREATED_DB",
                 f"Gasto creado en DB exitosamente: expense_id={expense.id}, amount={expense.amount} {expense.currency}",
                 error_code=ErrorCodes.OP_SUCCESS)
    return expense


def format_payment_receipt(expense: Expense) -> str:
    """
    Formatea un comprobante de pago detallado
    
    Args:
        expense: Objeto Expense que fue pagado
        
    Returns:
        Mensaje formateado con el comprobante
    """
    from datetime import date, datetime
    
    payer_name = expense.payer.name if expense.payer else "Usuario"
    debtor_name = expense.debtor.name if expense.debtor else "Usuario"
    
    message = (
        f"🧾 <b>COMPROBANTE DE PAGO</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Monto Pagado:</b> {expense.amount} {expense.currency}\n"
        f"📝 <b>Concepto:</b> {expense.description}\n"
        f"👤 <b>Pagado a:</b> {payer_name}\n"
        f"💳 <b>Pagado por:</b> {debtor_name}\n"
    )
    
    if expense.category:
        message += f"🏷️ <b>Categoría:</b> {expense.category}\n"
    
    if expense.due_date:
        message += f"📅 <b>Fecha de Vencimiento:</b> {expense.due_date.strftime('%d/%m/%Y')}\n"
    
    # Fecha y hora del pago
    payment_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    message += (
        f"🕐 <b>Fecha de Pago:</b> {payment_date}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ <b>Estado:</b> PAGADO"
    )
    
    return message


def format_expense_confirmation(expense: Expense) -> str:
    """
    Formata un mensaje de confirmación para un gasto registrado
    
    Args:
        expense: Objeto Expense
        
    Returns:
        Mensaje formateado
    """
    from datetime import date
    
    payer_name = expense.payer.name if expense.payer else "Usuario"
    debtor_name = expense.debtor.name if expense.debtor else "Usuario"
    
    message = (
        f"✅ <b>Gasto registrado</b>\n\n"
        f"💰 Monto: {expense.amount} {expense.currency}\n"
        f"📝 Descripción: {expense.description}\n"
        f"👤 Pagó: {payer_name}\n"
        f"💳 Debe: {debtor_name}\n"
    )
    
    if expense.category:
        message += f"🏷️ Categoría: {expense.category}\n"
    
    # Agregar fecha de vencimiento si existe
    if expense.due_date:
        today = date.today()
        if expense.due_date < today:
            message += f"📅 Fecha: {expense.due_date.strftime('%d/%m/%Y')} ⚠️ Vencida\n"
        elif expense.due_date == today:
            message += f"📅 Fecha: {expense.due_date.strftime('%d/%m/%Y')} 🔴 Vence hoy\n"
        else:
            message += f"📅 Fecha: {expense.due_date.strftime('%d/%m/%Y')}\n"
    
    return message


def get_user_expenses(user_id: int):
    """
    Obtiene todos los gastos relacionados con un usuario
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Tupla (expenses_to_pay, expenses_to_collect)
        - expenses_to_pay: Lista de gastos donde el usuario es deudor (debe pagar)
        - expenses_to_collect: Lista de gastos donde el usuario es pagador (debe cobrar)
    """
    # Gastos donde el usuario debe pagar (es deudor)
    expenses_to_pay = Expense.query.filter(
        Expense.debtor_id == user_id,
        Expense.is_settled == False
    ).order_by(Expense.created_at.desc()).all()
    
    # Gastos donde el usuario debe cobrar (es pagador)
    expenses_to_collect = Expense.query.filter(
        Expense.payer_id == user_id,
        Expense.is_settled == False
    ).order_by(Expense.created_at.desc()).all()
    
    return expenses_to_pay, expenses_to_collect


def get_user_debts_to_pay(user_id: int):
    """
    Obtiene solo las deudas que el usuario debe pagar
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Lista de gastos donde el usuario es deudor (debe pagar)
    """
    # Ordenar por fecha de vencimiento (las que tienen fecha primero, luego las que no tienen)
    # Usar una consulta más simple: primero las que tienen fecha, luego las que no
    from sqlalchemy import desc
    
    # Obtener todas las deudas
    all_debts = Expense.query.filter(
        Expense.debtor_id == user_id,
        Expense.is_settled == False
    ).all()
    
    # Ordenar manualmente: primero las que tienen due_date, ordenadas por fecha ascendente
    # luego las que no tienen due_date, ordenadas por created_at descendente
    debts_with_date = sorted(
        [d for d in all_debts if d.due_date is not None],
        key=lambda x: (x.due_date, x.created_at)
    )
    debts_without_date = sorted(
        [d for d in all_debts if d.due_date is None],
        key=lambda x: x.created_at,
        reverse=True
    )
    
    return debts_with_date + debts_without_date


def get_user_debts_to_collect(user_id: int):
    """
    Obtiene solo las deudas que el usuario debe cobrar (donde es pagador)
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Lista de gastos donde el usuario es pagador (debe cobrar)
    """
    from sqlalchemy import desc
    
    # Obtener todas las deudas a cobrar
    all_debts = Expense.query.filter(
        Expense.payer_id == user_id,
        Expense.is_settled == False
    ).all()
    
    # Ordenar manualmente: primero las que tienen due_date, ordenadas por fecha ascendente
    # luego las que no tienen due_date, ordenadas por created_at descendente
    debts_with_date = sorted(
        [d for d in all_debts if d.due_date is not None],
        key=lambda x: (x.due_date, x.created_at)
    )
    debts_without_date = sorted(
        [d for d in all_debts if d.due_date is None],
        key=lambda x: x.created_at,
        reverse=True
    )
    
    return debts_with_date + debts_without_date


def format_debts_to_collect(debts: list) -> str:
    """
    Formatea una lista de deudas que el usuario debe cobrar
    
    Args:
        debts: Lista de objetos Expense (deudas a cobrar)
        
    Returns:
        Mensaje formateado con la lista
    """
    from datetime import date
    
    if not debts:
        return "✅ No tienes deudas pendientes por cobrar."
    
    message = "💰 <b>Quién te debe:</b>\n\n"
    
    # Calcular totales por moneda
    from collections import defaultdict
    totals_by_currency = defaultdict(float)
    
    for idx, debt in enumerate(debts, 1):
        debtor_name = debt.debtor.name if debt.debtor else "Usuario"
        due_date_str = ""
        
        if debt.due_date:
            today = date.today()
            if debt.due_date < today:
                due_date_str = f" ⚠️ Vencida ({debt.due_date.strftime('%d/%m/%Y')})"
            elif debt.due_date == today:
                due_date_str = f" 🔴 Vence hoy"
            else:
                due_date_str = f" 📅 {debt.due_date.strftime('%d/%m/%Y')}"
        
        message += (
            f"<b>{idx}.</b> {debtor_name} te debe\n"
            f"   💰 {debt.amount} {debt.currency}\n"
            f"   📝 {debt.description}{due_date_str}\n\n"
        )
        
        totals_by_currency[debt.currency] += float(debt.amount)
    
    # Agregar totales
    if totals_by_currency:
        message += "\n<b>💰 Total a cobrar:</b>\n"
        for currency, total in totals_by_currency.items():
            message += f"• {total:,.2f} {currency}\n"
    
    return message


def mark_expense_as_paid(expense_id: int) -> Optional[Expense]:
    """
    Marca un gasto como pagado
    
    Args:
        expense_id: ID del gasto
        
    Returns:
        Objeto Expense actualizado o None si no se encuentra
    """
    log_operation(logger, "EXPENSE_MARK_PAID",
                 f"Marcando gasto como pagado: expense_id={expense_id}",
                 error_code=ErrorCodes.OP_SUCCESS)
    
    expense = Expense.query.get(expense_id)
    if expense:
        expense.is_settled = True
        db.session.commit()
        
        log_operation(logger, "EXPENSE_MARKED_PAID",
                     f"Gasto marcado como pagado exitosamente: expense_id={expense.id}, amount={expense.amount} {expense.currency}",
                     error_code=ErrorCodes.OP_SUCCESS)
        return expense
    else:
        log_error(logger, ErrorCodes.ERR_EXPENSE_NOT_FOUND,
                 f"Gasto no encontrado: expense_id={expense_id}",
                 exception=None)
    return None


def delete_expense(expense_id: int) -> Optional[Expense]:
    """
    Elimina un gasto de la base de datos (marcado como pagado)
    
    Args:
        expense_id: ID del gasto
        
    Returns:
        Objeto Expense eliminado o None si no se encuentra
    """
    log_operation(logger, "EXPENSE_DELETE",
                 f"Eliminando gasto de la base de datos: expense_id={expense_id}",
                 error_code=ErrorCodes.OP_SUCCESS)
    
    expense = Expense.query.get(expense_id)
    if expense:
        # Guardar referencias antes de eliminar para el comprobante
        # Necesitamos acceder a las relaciones antes de eliminar
        payer_ref = expense.payer
        debtor_ref = expense.debtor
        amount_val = expense.amount
        currency_val = expense.currency
        description_val = expense.description
        payer_id_val = expense.payer_id
        debtor_id_val = expense.debtor_id
        category_val = expense.category
        due_date_val = expense.due_date
        
        # Crear un objeto temporal con los datos (solo para el comprobante)
        # No podemos crear un Expense real sin guardarlo en la DB, así que usamos un objeto simple
        class ExpenseCopy:
            def __init__(self):
                self.amount = amount_val
                self.currency = currency_val
                self.description = description_val
                self.payer_id = payer_id_val
                self.debtor_id = debtor_id_val
                self.category = category_val
                self.due_date = due_date_val
                self.payer = payer_ref
                self.debtor = debtor_ref
        
        expense_copy = ExpenseCopy()
        
        # Eliminar de la base de datos
        db.session.delete(expense)
        db.session.commit()
        
        log_operation(logger, "EXPENSE_DELETED",
                     f"Gasto eliminado exitosamente: expense_id={expense_id}, amount={amount_val} {currency_val}",
                     error_code=ErrorCodes.OP_SUCCESS)
        return expense_copy
    else:
        log_error(logger, ErrorCodes.ERR_EXPENSE_NOT_FOUND,
                 f"Gasto no encontrado para eliminar: expense_id={expense_id}",
                 exception=None)
    return None


def format_debts_list_for_payment(debts: list) -> tuple[str, dict]:
    """
    Formatea una lista de deudas para mostrar con botones inline
    
    Args:
        debts: Lista de objetos Expense (deudas)
        
    Returns:
        Tupla (mensaje_texto, reply_markup) con el mensaje y los botones
    """
    from datetime import date
    
    if not debts:
        return "✅ No tienes deudas pendientes para pagar.", {}
    
    message = "💳 <b>Deudas Pendientes - Selecciona una para pagar:</b>\n\n"
    
    # Crear botones inline
    inline_keyboard = []
    
    for idx, debt in enumerate(debts, 1):
        payer_name = debt.payer.name if debt.payer else "Usuario"
        due_date_str = ""
        if debt.due_date:
            today = date.today()
            if debt.due_date < today:
                due_date_str = f" ⚠️ Vencida ({debt.due_date.strftime('%d/%m/%Y')})"
            elif debt.due_date == today:
                due_date_str = f" 🔴 Vence hoy"
            else:
                due_date_str = f" 📅 {debt.due_date.strftime('%d/%m/%Y')}"
        
        message += (
            f"<b>{idx}.</b> {debt.amount} {debt.currency} - {debt.description}\n"
            f"   👤 A: {payer_name}{due_date_str}\n\n"
        )
        
        # Crear botón para cada deuda
        button_text = f"{idx}. {debt.amount} {debt.currency} - {debt.description[:30]}"
        if len(debt.description) > 30:
            button_text += "..."
        
        inline_keyboard.append([{
            'text': button_text,
            'callback_data': f'pay_debt_{debt.id}'
        }])
    
    reply_markup = {
        'inline_keyboard': inline_keyboard
    }
    
    return message, reply_markup


def format_expenses_summary(user: User, expenses_to_pay: list, expenses_to_collect: list) -> str:
    """
    Formatea un resumen de gastos del usuario
    
    Args:
        user: Objeto User
        expenses_to_pay: Lista de gastos que el usuario debe pagar
        expenses_to_collect: Lista de gastos que el usuario debe cobrar
        
    Returns:
        Mensaje formateado con el resumen
    """
    from collections import defaultdict
    from datetime import date
    
    # Calcular totales por moneda para lo que debe pagar
    totals_to_pay = defaultdict(float)
    for expense in expenses_to_pay:
        totals_to_pay[expense.currency] += float(expense.amount)
    
    # Calcular totales por moneda para lo que debe cobrar
    totals_to_collect = defaultdict(float)
    for expense in expenses_to_collect:
        totals_to_collect[expense.currency] += float(expense.amount)
    
    message = f"📊 <b>Resumen de Gastos - {user.name}</b>\n\n"
    
    # Sección: Lo que debe pagar
    message += "💳 <b>Debes Pagar:</b>\n"
    if expenses_to_pay:
        for expense in expenses_to_pay:
            payer_name = expense.payer.name if expense.payer else "Usuario"
            status = "✅ Pagado" if expense.is_settled else "⏳ Pendiente"
            due_date_str = ""
            if expense.due_date:
                today = date.today()
                if expense.due_date < today:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')} ⚠️ Vencida"
                elif expense.due_date == today:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')} 🔴 Vence hoy"
                else:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')}"
            
            message += (
                f"• {expense.amount} {expense.currency} - {expense.description}\n"
                f"  👤 A: {payer_name}"
            )
            if expense.category:
                message += f" | 🏷️ {expense.category}"
            message += f"{due_date_str} | {status}\n"
    else:
        message += "✅ No tienes deudas pendientes\n"
    
    # Totales de lo que debe pagar
    if totals_to_pay:
        message += "\n<b>Total a pagar:</b>\n"
        for currency, total in totals_to_pay.items():
            message += f"• {total:.2f} {currency}\n"
    
    message += "\n"
    
    # Sección: Lo que debe cobrar
    message += "💰 <b>Debes Cobrar:</b>\n"
    if expenses_to_collect:
        for expense in expenses_to_collect:
            debtor_name = expense.debtor.name if expense.debtor else "Usuario"
            status = "✅ Pagado" if expense.is_settled else "⏳ Pendiente"
            due_date_str = ""
            if expense.due_date:
                today = date.today()
                if expense.due_date < today:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')} ⚠️ Vencida"
                elif expense.due_date == today:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')} 🔴 Vence hoy"
                else:
                    due_date_str = f" | 📅 {expense.due_date.strftime('%d/%m/%Y')}"
            
            message += (
                f"• {expense.amount} {expense.currency} - {expense.description}\n"
                f"  👤 De: {debtor_name}"
            )
            if expense.category:
                message += f" | 🏷️ {expense.category}"
            message += f"{due_date_str} | {status}\n"
    else:
        message += "ℹ️ No tienes gastos por cobrar\n"
    
    # Totales de lo que debe cobrar
    if totals_to_collect:
        message += "\n<b>Total a cobrar:</b>\n"
        for currency, total in totals_to_collect.items():
            message += f"• {total:.2f} {currency}\n"
    
    # Balance neto por moneda
    all_currencies = set(list(totals_to_pay.keys()) + list(totals_to_collect.keys()))
    if all_currencies:
        message += "\n<b>Balance Neto:</b>\n"
        for currency in all_currencies:
            net = totals_to_collect.get(currency, 0) - totals_to_pay.get(currency, 0)
            if net > 0:
                message += f"• Te deben: {net:.2f} {currency}\n"
            elif net < 0:
                message += f"• Debes: {abs(net):.2f} {currency}\n"
            else:
                message += f"• {currency}: En equilibrio\n"
    
    return message
