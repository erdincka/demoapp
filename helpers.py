import asyncio
import json
import logging
import os
import tarfile
import timeit
from faker import Faker

from nicegui import events, ui, app
import requests

from streams import produce

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
    files = ["/opt/mapr/conf/mapr-clusters.conf", "/opt/mapr/conf/ssl_truststore", "/opt/mapr/conf/ssl_truststore", "/root/jwt_access", "/root/jwt_refresh"]
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



def upload_client_files(e: events.UploadEventArguments):
    # possibly a security issue to use uploaded file names directly - don't care in demo/lab environment
    try:
        filename = e.name
        with open(f"/tmp/{filename}", "wb") as f:
            f.write(e.content.read())
        
        with tarfile.open(f"/tmp/{filename}", "r") as tf:
            if "config" in filename:
                tf.extractall(path="/opt/mapr")
                get_clusters()

            elif "jwt_tokens" in filename:
                tf.extractall(path="/root")
            else:
                ui.notify(f"Unknown filename: {filename}", type="warning")
                return

            ui.notify(f"{filename} extracted: {','.join(tf.getnames())}", type="positive")

    except Exception as error:
        ui.notify(error, type="negative")


def get_clusters():
    with open("/opt/mapr/conf/mapr-clusters.conf", "r") as conf:
        # reset the clusters
        app.storage.general["clusters"] = {}
        for line in conf.readlines():
            t = line.split(' ')
            # dict { 'value1': 'name1' } formatted cluster list, compatible to ui.select options
            cls = { t[2].split(":")[0] : t[0] }
            print(cls)
            app.storage.general["clusters"].update(cls)
            print(app.storage.general["clusters"])


def get_volumes():

    ip = app.storage.general['cluster']
    name = app.storage.general['clusters'][app.storage.general['cluster']]
    print(AUTH_CREDENTIALS)
    REST_URL = f"https://{ip}:8443/rest/volume/list?cluster={name}"

    try:
        vol_response = requests.get(url=REST_URL, auth=AUTH_CREDENTIALS, verify=False)
        vol_response.raise_for_status()

    except Exception as error:
        logger.warning(error)

    if vol_response:
            result = vol_response.json()
            logger.debug("volume info: %s", result)
            app.storage.general["volumes"] = result

    else:
        logger.warning("Cannot get volume info")


def stream_messages():
    fake = Faker("en_US")
    transactions = []

    count = 100

    for i in range(count):
        transactions.append(
            {
                "id": i + 1,
                "sender_account": fake.iban(),
                "receiver_account": fake.iban(),
                "amount": round(fake.pyint(0, 10_000), 2),
                "currency": "GBP",  # fake.currency_code(),
                "transaction_date": fake.past_datetime(start_date="-12M").timestamp(),
            }
        )

    # logger.debug("Creating monitoring table")
    stream_path = f"/apps/mystream"

    logger.info("Sending %s messages to %s:%s", len(transactions), stream_path, 'topic')

    tic = timeit.default_timer()

    for msg in transactions:
        produce(stream_path, "mytopic", json.dumps(msg))

    logger.info("It took %i seconds", timeit.default_timer() - tic)

