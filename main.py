#!/usr/bin/env python3
import inspect
import logging
import platform
import random

from nicegui import ui, app

from helpers import *
from functions import *
import ingest, modals, eventstore

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

app.on_exception(gracefully_fail)

@ui.page(path="/", title="DF Demo")
async def home():

    # reset the cluster info
    if "clusters" not in app.storage.general:
        app.storage.general["clusters"] = []
 
    with ui.row().classes('w-full bg-gray p-2 g-2 items-center justify-between'):
        ui.label(f"{APP_NAME}: {TITLE}").classes("text-xl")
        ui.space()
        ui.label().classes("uppercase").bind_text_from(app.storage.general, "cluster")
        target=f"https://{os.environ.get('MAPR_USER', 'mapr')}:{os.environ.get('MAPR_PASS', 'mapr123')}@{app.storage.general.get('cluster', 'localhost')}:8443/"
        ui.space()
        ui.switch("Show code").bind_value(app.storage.general, "showcode")
        ui.switch("Basics").bind_value(app.storage.general, "basics")
    
    with ui.row().classes("w-full"): # .bind_visibility_from(app.storage.general, "client_configured", backward=lambda x: not x):
        ui.upload(label="Client files", on_upload=upload_client_files, multiple=True, auto_upload=True, max_files=2).props("accept='application/x-tar,application/x-gzip' hide-upload-btn")
        ui.button("Configure client", on_click=lambda: run_command("/opt/mapr/server/configure.sh -R"))
        ui.button("Test command", on_click=lambda: run_command("env"))

    with ui.splitter(limits=(25,75)).classes("w-full") as splitter:
        with splitter.before:
            ui.markdown("SaaS platform for the hybrid enterprise with data distributed from edge to core to cloud. The federated global namespace integrates files, objects, and streaming data and offers consumption-based pricing. Far-flung deployments run in a single, logical view no matter where the data is located.")
            ui.image("./docs/global_namesp_clouds.png")

        with splitter.after:
            with ui.card().classes("w-full").bind_visibility(app.storage.general, "basics"):
                ui.label("Multi Modal").classes("text-xl")
                with ui.card_section():
                    ui.label("Filesystem")
                    ui.label("Touch a file in cluster filesystem using Posix mount path")
                    ui.code(inspect.getsource(modals.filesystem)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                    with ui.row().classes("items-center"):
                        cls = ui.select(options=app.storage.general["clusters"]).bind_value(app.storage.general, "cluster")
                        fn = ui.input("Filename")
                        ui.button("Run", on_click=lambda c=cls, f=fn: modals.filesystem(c.value, f.value))

                with ui.card_section():
                    ui.label("Object Store")
                    ui.label("Put a randomly generated data into a file in a bucket of choice")
                    ui.code(inspect.getsource(modals.objectstore)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                    with ui.row().classes("items-center"):
                        bucket = ui.input("Bucket")
                        fn = ui.input("Filename")
                        data = ui.label(random.random())
                        ui.button("Run", on_click=lambda b=bucket, f=fn, d=data: modals.objectstore(b.value, f.value, d))

                with ui.card_section():
                    ui.label("NoSQL Database")
                    ui.label("Write a json record to a table")
                    ui.code(inspect.getsource(modals.nosqldb)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                    with ui.row().classes("items-center"):
                        table = ui.input("Table")
                        data = ui.label(random.random())
                        ui.button("Run", on_click=lambda t=table, d=data: modals.objectstore(t.value, d))

                with ui.card_section():
                    ui.label("Streams")
                    ui.label("Push data using event store")
                    ui.code(inspect.getsource(modals.nosqldb)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                    with ui.row().classes("items-center"):
                        stream = ui.input("Stream:Topic")
                        data = ui.label(random.random())
                        ui.button("Run", on_click=lambda s=stream, d=data: modals.stream(s.value, d))

            with ui.card().classes("w-full").bind_visibility(app.storage.general, "basics"):
                ui.label("Multi Protocol").classes("text-xl")
                ui.label("HDFS")
                ui.code(inspect.getsource(ingest.hdfs)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                ui.button("Run")
                ui.label("RESTful")
                ui.code(inspect.getsource(ingest.restful)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                ui.button("Run")
                ui.label("NoSQL Database")
                ui.code(inspect.getsource(ingest.nosql)).classes("w-full text-wrap").bind_visibility_from(app.storage.general, "showcode")
                ui.button("Run")

            with ui.card().classes("w-full"):
                with ui.row().classes("w-full place-items-center"):
                    clusters = ui.select(options=app.storage.general["clusters"]).bind_value(app.storage.general, "cluster")
                    ui.button("Refresh", on_click=clusters.update)
                    ui.space()
                    ui.label().bind_text_from(app.storage.general, "cluster")

                # ui.button("Get volumes", on_click=get_volumes)
                # ui.table(
                #     title="Volumes",
                #     columns=[
                #         {
                #             "name": "name",
                #             "label": "Name",
                #             "field": "volid",
                #             "required": True,
                #             "align": "left",
                #         },
                #         {
                #             "name": "mountdir",
                #             "label": "Mounted",
                #             "field": "mountdir",
                #         }
                #     ],
                #     rows=[],
                #     row_key="volid",
                #     pagination=0,
                # ).on("rowClick", lambda e: print(e.args[1])).props("dense separator=None wrap-cells flat bordered virtual-scroll").classes("w-full").style("height: 300px")

                ui.button("Stream", on_click=stream_messages)
                ui.code(inspect.getsource(eventstore.produce))

# check if already configured
app.storage.general["client_configured"] = is_configured()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Demo",
        dark=None,
        port=3000,
        storage_secret="Ezmer@lR0cks",
        # NOTE: On Windows reload must be disabled to make asyncio.create_subprocess_exec work (see https://github.com/zauberzeug/nicegui/issues/486)
        reload=platform.system() != 'Windows')
