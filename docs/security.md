# Políticas de Seguridad del Chatbot

Este documento detalla las configuraciones y prácticas de seguridad implementadas en el proyecto para proteger la integridad del sistema y los datos de los usuarios.

## 1. Validación de Entrada (Input Validation)

Para prevenir ataques de inyección de código (como SQL Injection, Command Injection o XSS) y asegurar que el procesamiento de lenguaje natural reciba datos limpios, se ha implementado un sistema estricto de validación de mensajes.

### Lista Blanca de Caracteres (Allowlist)
El sistema utiliza una estrategia de "lista blanca", permitiendo únicamente un conjunto específico de caracteres seguros. Cualquier mensaje que contenga un carácter no incluido en esta lista será rechazado.

**Caracteres Permitidos:**
*   **Alfanuméricos:** Letras (`a-z`, `A-Z`) y números (`0-9`).
*   **Espacios:** Espacios en blanco y saltos de línea.
*   **Caracteres Especiales:** Únicamente se permiten:
    *   `$` (Signo de pesos/dólar)
    *   `,` (Coma)
    *   `.` (Punto)
*   **Caracteres Internacionales:** Se permite el set completo de caracteres del español:
    *   Vocales acentuadas (`á`, `é`, `í`, `ó`, `ú`, `Á`, `É`, `Í`, `Ó`, `Ú`)
    *   Letra eñe (`ñ`, `Ñ`)
    *   Diéresis (`ü`, `Ü`)

### Comportamiento del Sistema
Si un usuario envía un mensaje que contiene caracteres prohibidos (por ejemplo: `(`, `)`, `;`, `'`, `"`, `<`, `>`), el bot:
1.  **Rechaza el procesamiento:** No envía el texto a la API de Gemini ni a la base de datos.
2.  **Notifica al usuario:** Envía el mensaje: *"🚫 Tu mensaje no cumple con las politicas de seguridad"*.
3.  **Registra el evento:** Genera un log de error con código `INVALID_DATA` para auditoría.

## 2. Gestión de Secretos

*   **Variables de Entorno:** Todas las credenciales sensibles (API Keys de Gemini, Token de Telegram, URL de Base de Datos) se manejan exclusivamente a través de variables de entorno.
*   **No Hardcoding:** No existen credenciales hardcodeadas en el código fuente.

## 3. Logging y Auditoría

El sistema implementa un logging estructurado que permite rastrear:
*   Intentos de acceso no autorizado.
*   Mensajes rechazados por políticas de seguridad.
*   Errores en operaciones críticas (pagos, registro de gastos).

Cada log incluye:
*   Timestamp
*   Nivel de severidad
*   Código de error estandarizado
*   ID del usuario (si está disponible)
*   Origen de la solicitud

