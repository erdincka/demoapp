#!/usr/bin/env python3
import inspect
import logging
import platform

import importlib_resources
from nicegui import ui, app

from helpers import is_configured, run_command, upload_client_files, gracefully_fail
import ingest, modals

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app.on_exception(gracefully_fail)

@ui.page(path="/", title="DF Demo")
async def home():

    with ui.row().classes("w-full"): # .bind_visibility_from(app.storage.general, "client_configured", backward=lambda x: not x):
        ui.upload(label="Client files", on_upload=upload_client_files, multiple=True, auto_upload=True, max_files=2).props("accept='application/x-tar,application/x-gzip' hide-upload-btn")
        ui.button("Configure client", on_click=lambda: run_command("/opt/mapr/server/configure.sh -R"))

    with ui.splitter(limits=(25,75)).classes("w-full") as splitter:
        with splitter.before:
            ui.markdown("SaaS platform for the hybrid enterprise with data distributed from edge to core to cloud. The federated global namespace integrates files, objects, and streaming data and offers consumption-based pricing. Far-flung deployments run in a single, logical view no matter where the data is located.")
            ui.image("./docs/global_namesp_clouds.png")

        with splitter.after:
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


# check if already configured
app.storage.general["client_configured"] = is_configured()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Demo",
        dark=None,
        port=3000,
        # NOTE: On Windows reload must be disabled to make asyncio.create_subprocess_exec work (see https://github.com/zauberzeug/nicegui/issues/486)
        reload=platform.system() != 'Windows')
