import threading
import json
from flask import request

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


@server.route('/push', methods=["POST"])
def push():
    lid = request.args.get('lid', type=str, default=None)
    return json.dumps(scheduler.push_next_block(lid=lid))


@server.route('/get_queue')
def get_queue():
    return json.dumps(scheduler.pending_work)


if __name__ == "__main__":
    server.run(port=CONFIG['port'])
