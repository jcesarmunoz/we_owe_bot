# 🤖 Guía de Uso - Chatbot de Gastos

# IMPORTANTE

¡Bienvenido a tu asistente personal para gestionar gastos y deudas compartidas! Este bot te ayuda a llevar un registro fácil y rápido de quién debe a quién.

## 🚀 Comenzando

### 1. Registro
Para empezar a usar el bot, simplemente envía el comando:
`/start`

Si es tu primera vez, el bot te registrará automáticamente.

> **Nota:** El bot requiere autorización. Si no estás autorizado, contacta al administrador.

## 📝 Registrando Gastos y Deudas

El bot entiende lenguaje natural. Puedes hablarle como a una persona.

### 💸 Gastos Compartidos ("Gasté")
Usa esto cuando tú pagas algo y otra persona te debe la mitad (o su parte).

*   **Formato:** "Gasté [monto] con [Persona] en [Concepto]"
*   **Ejemplos:**
    *   "Gasté 50000 con Julieth en el supermercado"
    *   "Pagué 20000 de la cena con Carlos"

> **¿Qué pasa aquí?** Tú eres el **cobrador** (te deben dinero) y la persona mencionada es el **deudor**.

### 📉 Deudas Personales ("Debo")
Usa esto cuando tú le debes dinero a alguien.

*   **Formato:** "Debo [monto] a [Persona] por [Concepto]"
*   **Ejemplos:**
    *   "Debo 15000 a Juan por el taxi"
    *   "Tengo que pagarle 100000 a María del arriendo"

> **¿Qué pasa aquí?** Tú eres el **deudor** (debes dinero) y la persona mencionada es el **cobrador**.

## 📊 Consultando tu Estado

Puedes ver en cualquier momento cómo van tus cuentas.

*   **Ver resumen general:**
    *   Escribe: "Ver mis gastos", "Resumen" o "Lista de gastos"
    *   El bot te mostrará cuánto debes y cuánto te deben en total.

*   **Ver quién te debe (Cobrar):**
    *   Escribe: "Quién me debe", "Cobrar" o "Me deben"
    *   Verás una lista de personas que te deben dinero.

*   **Ver qué debes (Pagar):**
    *   Escribe: "Mis deudas", "Pagar" o "Qué debo"
    *   Verás la lista de tus deudas pendientes.

## 💳 Pagando Deudas

Para registrar que ya pagaste una deuda:

1.  Escribe: **"Pagar"** o **"Mis deudas"**.
2.  El bot te mostrará una lista de tus deudas con botones.
3.  **Presiona el botón** correspondiente a la deuda que quieres pagar.
4.  ¡Listo! La deuda se marcará como pagada y recibirás un comprobante.

## 🛡️ Seguridad

Por tu seguridad, el bot solo acepta mensajes con:
*   Letras y números.
*   Signos básicos: `$` (pesos), `,` (coma), `.` (punto).
*   Tildes y eñes.

Si envías caracteres extraños (como paréntesis, comillas, etc.), el mensaje será rechazado.
