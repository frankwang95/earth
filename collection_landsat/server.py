import json

from collection_landsat.src.scheduler import Scheduler
from baseimage.config import CONFIG
from baseimage.flask import get_flask_server


server = get_flask_server()
scheduler = Scheduler()


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
