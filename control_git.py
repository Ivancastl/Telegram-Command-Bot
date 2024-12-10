import os
import shutil
import subprocess
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Solicitar al usuario su ID y token
USUARIO_AUTORIZADO = int(input("Ingresa tu ID de Telegram: "))
TOKEN = input("Ingresa el token de tu bot de Telegram: ")

# Variable para mantener la ruta actual y los procesos en ejecución
current_path = os.getcwd()
running_processes = {}

async def send_large_message(update, text):
    """Envía un mensaje grande dividiéndolo en partes más pequeñas."""
    max_length = 4096
    for i in range(0, len(text), max_length):
        await update.message.reply_text(text[i:i + max_length])

async def execute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_path, running_processes

    # Verificar si el usuario es autorizado
    if update.effective_user.id != USUARIO_AUTORIZADO:
        await update.message.reply_text("No tienes permiso para ejecutar comandos.")
        return

    # Obtener el comando del mensaje de Telegram
    command = ' '.join(context.args)

    # Verificar si el comando es 'cd'
    if command.startswith("cd "):
        path = command[3:].strip()  # Obtener la ruta después de 'cd'
        try:
            if path == "..":
                # Si el usuario desea moverse hacia atrás
                current_path = os.path.dirname(current_path)
                os.chdir(current_path)  # Cambiar el directorio actual
                await update.message.reply_text(f"Directorio cambiado a: {current_path}")
            else:
                # Cambiar a la nueva ruta especificada
                new_path = os.path.join(current_path, path)
                if os.path.isdir(new_path):
                    current_path = new_path
                    os.chdir(current_path)  # Cambiar el directorio actual
                    await update.message.reply_text(f"Directorio cambiado a: {current_path}")
                else:
                    await update.message.reply_text("El directorio no existe. Intenta de nuevo.")
        except Exception as e:
            await update.message.reply_text(f"Error al cambiar de directorio: {str(e)}")

    elif command.startswith("download "):
        file_or_folder_name = command[9:].strip()  # Nombre del archivo o carpeta a descargar
        path_to_download = os.path.join(current_path, file_or_folder_name)

        if os.path.isdir(path_to_download):
            # Si es un directorio, comprimirlo y enviarlo
            zip_path = f"{path_to_download}.zip"
            shutil.make_archive(path_to_download, 'zip', path_to_download)  # Comprimir la carpeta
            await update.message.reply_text(f"Carpeta '{file_or_folder_name}' comprimida. Preparando para enviar...")

            # Enviar el archivo comprimido
            with open(zip_path, "rb") as file:
                await update.message.reply_document(document=file)

            os.remove(zip_path)  # Eliminar el archivo ZIP después de enviarlo
        elif os.path.isfile(path_to_download):
            # Si es un archivo, enviarlo directamente
            with open(path_to_download, "rb") as file:
                await update.message.reply_document(document=file)
        else:
            await update.message.reply_text("La carpeta o archivo no existe en el directorio actual.")

    elif command.endswith(".py"):
        # Ejecutar el script Python y capturar el PID
        script_path = os.path.join(current_path, command.strip())  # Ruta completa al script
        try:
            process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pid = process.pid
            running_processes[pid] = process  # Guardar el proceso con su PID
            await update.message.reply_text(f"Script '{command}' ejecutándose en segundo plano. PID: {pid}")
        except Exception as e:
            await update.message.reply_text(f"Error al ejecutar el script: {str(e)}")

    elif command.startswith("stop "):
        pid_to_stop = int(command.split()[1])  # Obtener el PID desde el comando
        if pid_to_stop in running_processes:
            try:
                process = running_processes[pid_to_stop]
                process.terminate()  # Terminar el proceso
                del running_processes[pid_to_stop]  # Eliminar el proceso de la lista
                await update.message.reply_text(f"Proceso con PID {pid_to_stop} detenido.")
            except Exception as e:
                await update.message.reply_text(f"Error al detener el proceso: {str(e)}")
        else:
            await update.message.reply_text(f"No se encontró un proceso con PID {pid_to_stop}.")
    else:
        try:
            # Ejecutar el comando en el directorio actual
            result = os.popen(command).read()
            if result:
                await send_large_message(update, f"Resultado:\n{result}")
            else:
                await update.message.reply_text("El comando se ejecutó correctamente, pero no hubo salida.")
        except Exception as e:
            await update.message.reply_text(f"Error al ejecutar el comando: {str(e)}")

async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_path

    # Verificar si el usuario es autorizado
    if update.effective_user.id != USUARIO_AUTORIZADO:
        await update.message.reply_text("No tienes permiso para enviar archivos.")
        return

    # Verificar si se recibió un archivo
    document = update.message.document
    if document:
        file = await context.bot.get_file(document.file_id)  # Obtener el objeto File desde Telegram
        file_path = os.path.join(current_path, document.file_name)  # Definir la ruta completa
        await file.download_to_drive(file_path)  # Descargar el archivo a la ruta actual
        await update.message.reply_text(f"Archivo '{document.file_name}' guardado en: {current_path}")
    else:
        await update.message.reply_text("No se encontró un archivo para guardar.")

# Configurar el bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("cmd", execute_command))
app.add_handler(MessageHandler(filters.Document.ALL, save_file))  # Manejar archivos

app.run_polling()
