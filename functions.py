import logging
import tarfile
import json
import timeit
from faker import Faker

from nicegui import events, ui, app

from eventstore import produce

logger = logging.getLogger()

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
            app.storage.general["clusters"].update(cls)


# def get_volumes():

#     ip = app.storage.general['cluster']
#     name = app.storage.general['clusters'][app.storage.general['cluster']]
#     REST_URL = f"https://{ip}:8443/rest/volume/list?cluster={name}"

#     try:
#         vol_response = requests.get(url=REST_URL, auth=AUTH_CREDENTIALS, verify=False)
#         vol_response.raise_for_status()

#     except Exception as error:
#         logger.warning(error)

#     if vol_response:
#             app.storage.general["volumes"] = []
#             result = vol_response.json()
#             for vol in result["data"]:
#                 logger.warning("volume found: %s", vol["volumename"])
#                 app.storage.general["volumes"].append({"volid": vol["volumename"], "mountdir": vol["mountdir"]})

#     else:
#         logger.warning("Cannot get volume info")


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

