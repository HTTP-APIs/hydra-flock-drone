"""Script to handle all operations related to anomalies."""
from hydra import SCHEMA
from flock_drone.mechanics.main import RES_CS, CENTRAL_SERVER
from flock_drone.mechanics.logs import (send_http_api_log, gen_HttpApiLog,
                                        send_dronelog, gen_DroneLog)


def gen_Anomaly(location):
    """Generate an anomaly object."""
    anomaly = {
        "@type": "Anomaly",
        "Location": location
    }

    return anomaly


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
