# 🤖 Guía de Uso - Chatbot de Gastos

# IMPORTANTE

Por favor leer los comentarios de la actividad y lo siguiente:

> Buena noche, Estimado Profesor Miguel
>
> Mi proyecto final de este curso de construcción de aplicaciones con IA fue un chatbot en telegram que permite registrar gastos, listarlos, y llevar un control de pago y deuda, el back fue desarrollado en python con flask y fue desplegado en vercel con la base de datos en postgres.
>
> Para utilizarlo es sencillo en telegram busque el bot llamado **MisGastosBot** le da unirse y posteriormente `/start`, ya con esto registra su usuario en base de datos, como primer chat puede agregar:
>
> *"debo a J Cesar Muñoz 15000 por cena"*
>
> Y creará el registro. Para listar coloca "pagar" y listara lo que debe y puede seleccionar que pagar según una lista desplegable que se ve debajo de la lista, por ultimo creara un comprobante de lo que pago, si desea saber a quién debe colocar algo referente a deudas o a quien debo ya que se utiliza gemini nuestra LLM interpretará lo que se escribe para que sea entendible por el back.
>
> Adjunto url del repositorio en github:
> [jcesarmunoz/we_owe_bot](https://github.com/jcesarmunoz/we_owe_bot)


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
