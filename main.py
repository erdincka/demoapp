#!/usr/bin/env python3
import asyncio
import inspect
import logging
import os.path
import platform
import shlex
import sys

from nicegui import ui, app

import ingest, modals

logger = logging.basicConfig()

# Handle exceptions without UI failure
def gracefully_fail(exc: Exception):
    print("gracefully failing...")
    logger.exception(exc)

app.on_exception(gracefully_fail)


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
    result = ui.markdown()

with ui.row().classes("w-full"):
    with ui.card():
        ui.label("Multi Modal").classes("text-xl")
        ui.label("Posix / NFS File System")
        ui.code(inspect.getsource(getattr(modals, "filesystem"))).classes("w-full text-wrap")
        ui.button("Run")
        ui.label("Object Store")
        ui.code(inspect.getsource(getattr(modals, "objectstore"))).classes("w-full text-wrap")
        ui.button("Run")
        ui.label("NoSQL Database")
        ui.code(inspect.getsource(getattr(modals, "nosqldb"))).classes("w-full text-wrap")
        ui.button("Run")


    with ui.card():
        ui.label("Multi Protocol").classes("text-xl")
        ui.label("HDFS")
        ui.code(inspect.getsource(getattr(ingest, "hdfs"))).classes("w-full text-wrap")
        ui.button("Run")
        ui.label("RESTful")
        ui.code(inspect.getsource(getattr(ingest, "restful"))).classes("w-full text-wrap")
        ui.button("Run")
        ui.label("NoSQL Database")
        ui.code(inspect.getsource(getattr(ingest, "nosql"))).classes("w-full text-wrap")
        ui.button("Run")


# ui.button('python3 hello.py', on_click=lambda: run_command('python3 hello.py')).props('no-caps')
# ui.button('python3 slow.py', on_click=lambda: run_command('python3 slow.py')).props('no-caps')
# with ui.row().classes('items-center'):
#     ui.button('python3 hello.py "<message>"', on_click=lambda: run_command(f'python3 hello.py "{message.value}"')) \
#         .props('no-caps')
#     message = ui.input('message', value='NiceGUI')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Demo",
        dark=None,
        port=3000,
        # NOTE: On Windows reload must be disabled to make asyncio.create_subprocess_exec work (see https://github.com/zauberzeug/nicegui/issues/486)
        reload=platform.system() != 'Windows')
