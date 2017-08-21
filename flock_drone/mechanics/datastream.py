"""Operation related to datastream post operations."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

import json
from flock_drone.mechanics.main import (RES_CS, RES_DRONE,
                                        CENTRAL_SERVER, DRONE)
from flock_drone.mechanics.logs import send_http_api_log, gen_HttpApiLog
from hydra import SCHEMA, Resource


# Datastream related methods
def gen_Datastream(temperature, position, drone_id):
    """Generate a datastream objects."""
    datastream = {
        "@type": "Datastream",
        "Temperature": temperature,
        "Position": position,
        "DroneID": drone_id,
    }

    return datastream


def send_datastream(datastream):
    """Post the drone current datastream to the central server."""
    try:
        drone_identifier = datastream["DroneID"]
        post_datastream = RES_CS.find_suitable_operation(
            SCHEMA.AddAction, CENTRAL_SERVER.Datastream)
        resp, body = post_datastream(datastream)

        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        print("Datastream posted successfully.")

        http_api_log = gen_HttpApiLog("Drone %s" % (
            str(drone_identifier)), "PUT Datastream", "Controller")
        send_http_api_log(http_api_log)

    except Exception as e:
        print(e)
        return None


def update_datastream(datastream):
    """Update the drone datastream on drone server."""
    try:
        update_datastream_ = RES_DRONE.find_suitable_operation(
            operation_type=SCHEMA.UpdateAction, input_type=DRONE.Datastream)
        resp, body = update_datastream_(datastream)
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        return Resource.from_iri(resp['location'])
    except Exception as e:
        print(e)
        return None


def add_datastream(datastream):
    """Update the drone datastream on drone server."""
    try:
        update_datastream_ = RES_DRONE.find_suitable_operation(
            operation_type=SCHEMA.AddAction, input_type=DRONE.Datastream)
        resp, body = update_datastream_(datastream)
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        return Resource.from_iri(resp['location'])
    except Exception as e:
        print(e)
        return None


def get_datastream():
    """Get the drone datastream from drone server."""
    try:
        get_datastream_ = RES_DRONE.find_suitable_operation(
            operation_type=None, input_type=None, output_type=DRONE.Datastream)
        resp, body = get_datastream_()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        datastream = json.loads(body.decode('utf-8'))
        # remove extra contexts from datastream
        datastream.pop("@context", None)
        datastream.pop("@id", None)
        return datastream
    except Exception as e:
        print(e)
        return None
