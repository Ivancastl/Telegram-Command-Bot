# Telegram Command Executor Bot

Este bot de Telegram permite ejecutar comandos, gestionar archivos y controlar procesos de manera remota en tu máquina.

## Características

- Cambia directorios en el sistema.
- Descarga archivos y carpetas.
- Sube archivos y Carpetas.
- Ejecuta scripts.
- Detiene procesos en ejecución.
- Descomprime Zip

## Requisitos

- Python
- python-telegram-bot

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/Ivancastl/Telegram-Command-Executor-Bot.git
    ```

2. Navega al directorio del proyecto:
    ```bash
   cd bot_remote
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configura el token y el usuario autorizado en el código.

5. Ejecuta el bot:
    ```bash
    python control.py
    ```

# Comandos disponibles:

- /cmd cd <ruta>: Cambia el directorio.
- /cmd download <archivo/carpeta>: Descarga un archivo o carpeta.
- /cmd <script.py>: Ejecuta un script Python.
- /cmd stop <PID>: Detiene un proceso en ejecución.
- /cmd <comando_del_sistema>: Ejecuta cualquier comando del sistema (por ejemplo, ls, mkdir, rm, etc.).
- Enviar archivo: Guarda un archivo enviado por el usuario.
