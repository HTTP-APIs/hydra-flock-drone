"""Operation related to datastream post operations."""
import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

from flock_drone.mechanics.main import RES_CS, RES_DRONE
from flock_drone.mechanics.main import CENTRAL_SERVER, DRONE
from flock_drone.mechanics.main import gen_DroneLog, gen_HttpApiLog
from hydra import SCHEMA, Resource


def send_dronelog(dronelog):
    """Post the drone log to the central server."""
    post_dronelog = RES_CS.find_suitable_operation(SCHEMA.AddAction, CENTRAL_SERVER.DroneLog)
    resp, body = post_dronelog(dronelog)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    new_dronelog = Resource.from_iri(resp['location'])
    print("Drone Log successfully.")
    return new_dronelog

def send_http_api_log(http_api_log):
    """Post the drone http Api Log to the central server."""
    post_http_api_log = RES_CS.find_suitable_operation(SCHEMA.AddAction, CENTRAL_SERVER.HttpApiLog)
    resp, body = post_http_api_log(http_api_log)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    new_http_api_log = Resource.from_iri(resp['location'])
    print("Http Api Log posted successfully.")
    return new_http_api_log

if __name__ == "__main__":
    dronelog = gen_DroneLog("upated position")
    print(send_dronelog(dronelog))
    http_api_log = gen_HttpApiLog("GET", "Controller Location")
    print(send_http_api_log(http_api_log))
