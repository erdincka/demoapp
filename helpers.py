import asyncio
import logging
import os

from nicegui import ui, app

logger = logging.getLogger()

APP_NAME = "Ezmeral"
TITLE = "Data Fabric"

AUTH_CREDENTIALS = (os.environ["MAPR_USER"], os.environ["MAPR_PASS"])


def toggle_debug(val: bool):
    if val:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


# Handle exceptions without UI failure
def gracefully_fail(exc: Exception):
    print("gracefully failing...")
    logger.warning(exc)


def is_configured():
    """
    Check if all client configuration files in place
    """
    files = ["/opt/mapr/conf/mapr-clusters.conf", "/opt/mapr/conf/ssl_truststore", "/opt/mapr/conf/ssl_truststore.pem", "/root/jwt_access", "/root/jwt_refresh"]
    return all([os.path.isfile(f) for f in files])


async def run_command(command: str) -> None:
    """Run a command in the background and display the output in the pre-created dialog."""
    with ui.dialog().props("full-width v-model='cmd") as dialog, ui.card().classes("grow relative"):
        ui.button(icon="close", on_click=dialog.close).props("flat round dense").classes("absolute right-4 top-4")
        result = ui.log().classes("w-full").style("white-space: pre-wrap")

    dialog.open()
    result.content = ''
    # command = command.replace('python3', sys.executable)  # NOTE replace with machine-independent Python path (#1240)
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    stdout, stderr = await process.communicate()
    if stdout:
        result.push(stdout.decode())
    if stderr:
        result.push(stderr.decode())
    # # NOTE we need to read the output in chunks, otherwise the process will block
    # while True:
    #     new = await process.stdout.read(4096)
    #     if not new:
    #         break
    #     result.push(new.decode())

