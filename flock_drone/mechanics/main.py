"""Handle main configuration for the drone."""
import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

import json
from hydra import Resource, SCHEMA
from rdflib import Namespace

from flock_drone.settings import CENTRAL_SERVER_NAMESPACE, DRONE_NAMESPACE
from flock_drone.settings import CENTRAL_SERVER_URL
from flock_drone.settings import IRI_CS, IRI_DRONE, DRONE_DEFAULT
import pdb
import time

from flock_drone.mechanics.logs import send_http_api_log, gen_HttpApiLog

global CENTRAL_SERVER, DRONE, RES_CS, RES_DRONE
CENTRAL_SERVER = Namespace(CENTRAL_SERVER_NAMESPACE)
DRONE = Namespace(DRONE_NAMESPACE)

RES_CS = Resource.from_iri(IRI_CS)
RES_DRONE = Resource.from_iri(IRI_DRONE)


def get_drone_default():
    """Return the default drone object from settings."""
    return DRONE_DEFAULT


def get_drone():
    """Get the drone object from drone server."""
    get_drone_ = RES_DRONE.find_suitable_operation(operation_type=None, input_type=None,
                                                   output_type=DRONE.Drone)
    resp, body = get_drone_()
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    drone = json.loads(body.decode('utf-8'))
    drone.pop("@id", None)
    drone.pop("@context", None)
    return drone


def get_controller_location():
    """Get the controller location from central server."""
    try:
        get_controller_location_ = RES_CS.find_suitable_operation(operation_type=None,
                                                                  input_type=None,
                                                                  output_type=CENTRAL_SERVER.Location)
        resp, body = get_controller_location_()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        location_obj = json.loads(body.decode('utf-8'))
        location_obj.pop("@context")
        location_obj.pop("@type")
        return location_obj
    except ConnectionRefusedError as e:
        print(e)
        print("Failed to use controller location, returning default")
        return "0,0"


def update_drone(drone):
    """Update the drone object on drone server."""
    drone_identifier = drone["DroneID"]
    try:
        update_drone_ = RES_DRONE.find_suitable_operation(operation_type=SCHEMA.UpdateAction,
                                                          input_type=DRONE.Drone)
        resp, body = update_drone_(drone)
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        return Resource.from_iri(resp['location'])
    except ConnectionRefusedError:
        raise ConnectionRefusedError("Connection Refused! Please check the drone server.")

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "POST DroneState", "Localhost")
    send_http_api_log(http_api_log)


def update_drone_at_controller(drone, drone_identifier):
    """Update the drone object at central controller."""
    id_ = "/api/DroneCollection/" + str(drone_identifier)
    try:
        print("Updating drone")
        RES = Resource.from_iri(CENTRAL_SERVER_URL + id_)
        operation = RES.find_suitable_operation(input_type=CENTRAL_SERVER.Drone)
        assert operation is not None
        resp, body = operation(drone)
        print(drone)
        assert resp.status in [200, 201]
    except Exception as e:
        print(e)
        print(drone, drone_identifier)
        # print("exception")
        return {404: "Resource with Id %s not found!" % (id_,)}

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "POST Drone", "Controller")
    send_http_api_log(http_api_log)


def ordered(obj):
    """Sort json dicts and lists within."""
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


if __name__ == "__main__":

    print(get_drone())
    drone = get_drone()
    drone_identifier = drone["DroneID"]
    print(drone_identifier)
    print(update_drone_at_controller(drone, drone_identifier))
    # print(update_drone(get_drone_default()))
    # print(get_drone_id())
    # datastream = gen_datastream(100, "0,0", get_drone_id())
    # print(update_datastream(datastream))
    # print(get_datastream())
    # state = gen_state(-1000, "50", "North", "1,1", "Active", 100)
    # print(state)
    # print(update_state(state))
    # print(get_state())
