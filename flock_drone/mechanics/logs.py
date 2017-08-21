"""Operation related to datastream post operations."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

from flock_drone.settings import CENTRAL_SERVER_NAMESPACE, IRI_CS
from hydra import SCHEMA, Resource
from rdflib import Namespace

CENTRAL_SERVER = Namespace(CENTRAL_SERVER_NAMESPACE)
RES_CS = Resource.from_iri(IRI_CS)


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
    try:
        post_dronelog = RES_CS.find_suitable_operation(
            SCHEMA.AddAction, CENTRAL_SERVER.DroneLog)
        resp, body = post_dronelog(dronelog)

        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        new_dronelog = Resource.from_iri(resp['location'])
        print("Drone Log successfully.")
        return new_dronelog
    except Exception as e:
        print(e)
        return None


def send_http_api_log(http_api_log):
    """Post the drone http Api Log to the central server."""
    try:
        post_http_api_log = RES_CS.find_suitable_operation(
            SCHEMA.AddAction, CENTRAL_SERVER.HttpApiLog)
        resp, body = post_http_api_log(http_api_log)

        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        new_http_api_log = Resource.from_iri(resp['location'])
        print("Http Api Log posted successfully.")
        return new_http_api_log
    except Exception as e:
        print(e)
        return None
