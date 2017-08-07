"""Script to handle all operations related to anomalies."""
import json
from hydra import SCHEMA
from flock_drone.mechanics.main import RES_CS, CENTRAL_SERVER, RES_DRONE, DRONE
from flock_drone.mechanics.logs import (send_http_api_log, gen_HttpApiLog,
                                        send_dronelog, gen_DroneLog)


def get_new_state(anomaly, drone):
    """Get the new state of the drone to move towards the anomaly."""
    pass


def gen_Anomaly(location):
    """Generate an anomaly object."""
    anomaly = {
        "@type": "Anomaly",
        "Location": location
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
    except ConnectionRefusedError:
        raise ConnectionRefusedError("Connection Refused! Please check the drone server.")


def send_anomaly(anomaly, drone_identifier):
    """Send the drone current datastream to the central server."""
    post_anomaly = RES_CS.find_suitable_operation(SCHEMA.AddAction, CENTRAL_SERVER.Anomaly)
    resp, body = post_anomaly(anomaly)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    print("Anomaly added successfully.")

    http_api_log = gen_HttpApiLog("Drone %s" % (str(drone_identifier)), "PUT Anomaly", "Controller")
    send_http_api_log(http_api_log)

    dronelog = gen_DroneLog("Drone %s" % (str(drone_identifier),),
                            "detected anomaly at %s" % (str(anomaly["Location"])))
    send_dronelog(dronelog)
