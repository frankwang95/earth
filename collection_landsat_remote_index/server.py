import json
import threading
from flask import request

from baseimage.config import CONFIG
from baseimage.flask import get_flask_server
from baseimage.logger.logger import get_default_logger

from collection_landsat_remote_index.src.worker import LandSatRemoteIndexTask
from collection_landsat_remote_index.src.block_generator import LandSatRemoteIndexBlockGenerator

from lib_learning.collection.workers.base_worker import Worker
from lib_learning.collection.scheduler import Scheduler
from lib_learning.collection.interfaces.local_interface import LocalInterface


# interface
interface = LocalInterface()

# workers
worker_logger = get_default_logger('worker')
lsrit = LandSatRemoteIndexTask(worker_logger, CONFIG['mysql'])
worker_thread = threading.Thread(target=Worker, args=(interface, lsrit.main, worker_logger))
worker_thread.setDaemon(True)
worker_thread.start()

# schedulers
scheduler_logger = get_default_logger('scheduler')
block_generator = LandSatRemoteIndexBlockGenerator(CONFIG['api_url'])
scheduler = Scheduler(
    'collection_landsat_remote_index', interface, block_generator, scheduler_logger,
    task_timeout=600, confirm_interval=10
)

# service server
server = get_flask_server()


@server.route('/push', methods=["POST"])
def push():
    row = request.args.get('row', type=int, default=None)
    path = request.args.get('path', type=int, default=None)
    assert type(row) == type(path)
    return json.dumps(scheduler.push_next_block(row=row, path=path))


@server.route('/get_queue')
def get_queue():
    return json.dumps(scheduler.pending_work)


if __name__ == "__main__":
    server.run(port=CONFIG['port'])
