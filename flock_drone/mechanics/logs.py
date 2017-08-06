"""Operation related to datastream post operations."""
from flock_drone.mechanics.main import RES_CS
from flock_drone.mechanics.main import CENTRAL_SERVER
from flock_drone.mechanics.main import get_drone
from hydra import SCHEMA, Resource


def gen_DroneLog(drone_id, log_string):
    """Generate a Drone log object from log string."""
    dronelog = {
        "@type": "DroneLog",
        "DroneID": drone_id,
        "LogString": log_string
    }
    return dronelog


def gen_HttpApiLog(source, action, target):
    """Generate a Http Api Log object from action and target."""
    httpapilog = {
        "@type": "HttpApiLog",
        "Subject": source,
        "Predicate": action,
        "Object": target
    }
    return httpapilog


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
    drone_id = get_drone()["DroneID"]
    dronelog = gen_DroneLog("Drone %s" % (str(drone_id)), "upated position")
    print(send_dronelog(dronelog))
    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_id)), "GET Location", "Controller")
    print(send_http_api_log(http_api_log))
