"""Script to handle all operations related to anomalies."""
import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

import json
from hydra import SCHEMA, Resource
from flock_drone.settings import CENTRAL_SERVER_URL
from flock_drone.mechanics.main import RES_CS, CENTRAL_SERVER, RES_DRONE, DRONE
from flock_drone.mechanics.logs import (send_http_api_log, gen_HttpApiLog,
                                        send_dronelog, gen_DroneLog)

def gen_Anomaly(location, id_):
    """Generate an anomaly object."""
    anomaly = {
        "@type": "Anomaly",
        "Location": location,
        "DroneID": id_,
        "Status": "To be Confirmed",
        "AnomalyID": "-1"
    }

    return anomaly



def get_anomaly():
    """Get the anomaly from drone server."""
    try:
        get_anomaly_ = RES_DRONE.find_suitable_operation(
            operation_type=None, input_type=None, output_type=DRONE.Anomaly)
        resp, body = get_anomaly_()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        anomaly = json.loads(body.decode('utf-8'))
        anomaly.pop("@context", None)
        anomaly.pop("@id", None)
        return anomaly
    except Exception as e:
        print(e)
        return None


def send_anomaly(anomaly, drone_identifier):
    """Send the detected anomaly to the central server."""
    post_anomaly = RES_CS.find_suitable_operation(SCHEMA.AddAction, CENTRAL_SERVER.Anomaly)
    resp, body = post_anomaly(anomaly)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    print("Anomaly added successfully.")
    body = json.loads(body.decode('utf-8'))

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "PUT Anomaly", "Controller")
    send_http_api_log(http_api_log)

    try:
        ## Get the anomaly_id from body
        anomaly_id = body[list(body.keys())[0]].split("=")[-1]
        print("ID assigned to anomaly is", anomaly_id)
        ## Update the anomalyID at central controller
        anomaly["AnomalyID"] = anomaly_id
        update_anomaly_at_controller(anomaly, anomaly_id, drone_identifier)
    except Exception as e:
        print(e)
        pass

    dronelog = gen_DroneLog("Drone %s" % (str(drone_identifier),),
                            "detected anomaly at %s" % (str(anomaly["Location"])))
    send_dronelog(dronelog)


def update_anomaly_at_controller(anomaly, anomaly_id, drone_identifier):
    """Update the anomaly object at central controller."""
    id_ = "/api/AnomalyCollection/" + str(anomaly_id)
    try:
        print("Updating anomaly")
        RES = Resource.from_iri(CENTRAL_SERVER_URL + id_)
        operation = RES.find_suitable_operation(operation_type=SCHEMA.UpdateAction)
        assert operation is not None
        print(anomaly)
        resp, body = operation(anomaly)
        assert resp.status in [200, 201]
    except Exception as e:
        print(e)
        return {404: "Resource with Id %s not found!" % (id_,)}

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "POST Anomaly", "Controller")
    send_http_api_log(http_api_log)

def update_anomaly_locally(anomaly, drone_identifier):
    """Update the anomaly object at local drone server."""
    id_ = "/api/Anomaly"
    try:
        print("Updating anomaly")
        RES = Resource.from_iri(DRONE_URL + id_)
        operation = RES.find_suitable_operation(operation_type=SCHEMA.UpdateAction)
        assert operation is not None
        print(anomaly)
        resp, body = operation(anomaly)
        assert resp.status in [200, 201]
    except Exception as e:
        print(e)
        return {404: "Resource with Id %s not found!" % (id_,)}

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "POST Anomaly", "Localhost")
    send_http_api_log(http_api_log)


if __name__ == "__main__":
    anomaly = gen_Anomaly("0,0", "-1000")
    send_anomaly(anomaly, "-1000")
