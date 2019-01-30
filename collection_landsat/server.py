import threading
import json

from baseimage.config import CONFIG
from baseimage.flask import get_flask_server
from baseimage.logger import get_default_logger

from collection_landsat.src.worker import LandSatLocalIndexTask
from collection_landsat.src.block_generator import LandSatLocalIndexBlockGenerator

from lib_learning.collection.workers.base_worker import Worker
from lib_learning.collection.scheduler import Scheduler
from lib_learning.collection.interfaces.local_interface import LocalInterface


# interface
interface = LocalInterface()

# workers
worker_logger = get_default_logger('worker')
lslit = LandSatLocalIndexTask(worker_logger, CONFIG['data_dir'], CONFIG['mysql'], CONFIG['google_api_url'])
worker_thread = threading.Thread(target=Worker, args=(interface, lslit.main, worker_logger))
worker_thread.setDaemon(True)
worker_thread.start()

# schedulers
scheduler_logger = get_default_logger('scheduler')
block_generator = LandSatLocalIndexBlockGenerator(CONFIG['mysql'])
scheduler = Scheduler(
    'collection_landsat', interface, block_generator, scheduler_logger,
    task_timeout=1800, confirm_interval=60
)

# service server
# TODO: endpoints here should be standardized and moved into lib_learning.collection
server = get_flask_server()


@server.route('/push/<lid>', methods=["POST"])
def push(lid):
    scheduler.push(lid)
    return "{}"


@server.route('/process_queue', methods=["GET"])
def get_process_queue():
    p_queue = scheduler.get_p_queue()
    response = {
        "p_queue_len": len(p_queue),
        "p_queue": p_queue
    }
    return json.dumps(response)


@server.route('/download_queue', methods=["GET"])
def get_download_queue():
    d_queue = scheduler.get_d_queue()
    response = {
        "d_queue_len": len(d_queue),
        "d_queue": d_queue
    }
    return json.dumps(response)


@server.route('/check_for_scene/<lid>', methods=["GET"])
def check_for_scene(lid):
    response = {
        "scene_id": lid,
        "is_present": scheduler.check_scene_exists(lid)
    }
    return json.dumps(response)


if __name__ == "__main__":
    server.run(port=CONFIG['port'])
