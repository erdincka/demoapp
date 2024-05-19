### Show simple examples on various data formats

from helpers import run_command


async def filesystem(cluster: str, filename: str):
    workdir = f"/edfs/{cluster}"
    # touch a file on cluster
    await run_command(f"ls -l {workdir} && touch {workdir}/{filename} && ls -l {workdir}")


async def objectstore(bucket: str, objectname: str):
    # create and PUT file to S3 endpoint
    print(f"Would happily create {objectname} in bucket: {bucket}")


async def nosqldb(tablename: str):
    print(f"Upsert {tablename}")


async def stream(stream: str, topic: str):
    print(f"Publish to {stream}:{topic}")


# MODALS = [
#     ("Posix / NFS File System", "filesystem"),
#     ("Object Store", "objectstore"),
#     ("NoSQL Database", "nosqldb"),
# ]

#     for modal in modals.MODALS:
#         modal_label, function_name = modal
#         func = getattr(modals, function_name)
#         ui.label(modal_label)
#         ui.code(inspect.getsource(func)).classes("w-full text-wrap")
#         with ui.row().classes("items-center"):
#             param = ui.input("Parameter", value=f"{function_name}_param")
#             ui.button("Run", on_click=lambda f=func, p=param: f(p.value))
#         ui.separator()
