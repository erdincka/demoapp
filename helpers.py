import asyncio
import logging
import os
import shlex
import sys
import tarfile

from nicegui import events, ui

logger = logging.getLogger()

# Handle exceptions without UI failure
def gracefully_fail(exc: Exception):
    print("gracefully failing...")
    logger.warning(exc)

def is_configured():
    """
    Check if all client configuration files in place
    """
    files = ["/opt/mapr/conf/mapr-clusters.conf", "/opt/mapr/conf/ssl_truststore", "/opt/mapr/conf/ssl_truststore", "/root/jwt_access", "/root/jwt_refresh"]
    return all([os.path.isfile(f) for f in files])


async def run_command(command: str) -> None:
    """Run a command in the background and display the output in the pre-created dialog."""
    dialog.open()
    result.content = ''
    command = command.replace('python3', sys.executable)  # NOTE replace with machine-independent Python path (#1240)
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command, posix='win' not in sys.platform.lower()),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    # NOTE we need to read the output in chunks, otherwise the process will block
    output = ''
    while True:
        new = await process.stdout.read(4096)
        if not new:
            break
        output += new.decode()
        # NOTE the content of the markdown element is replaced every time we have new output
        result.content = f'```\n{output}\n```'

with ui.dialog() as dialog, ui.card():
    result = ui.log()


def upload_client_files(e: events.UploadEventArguments):
    # possibly a security issue to use uploaded file names directly - don't care in demo/lab environment
    try:
        filename = e.name
        with open(f"/tmp/{filename}", "wb") as f:
            f.write(e.content.read())
        
        with tarfile.open(f"/tmp/{filename}", "r") as tf:
            if "config" in filename:
                tf.extractall(path="/opt/mapr")
            elif "jwt_tokens" in filename:
                tf.extractall(path="/root")
            else:
                ui.notify(f"Unknown filename: {filename}", type="warning")
                return

            ui.notify(f"{filename} extracted: {','.join(tf.getnames())}", type="positive")

    except Exception as error:
        ui.notify(error, type="negative")

