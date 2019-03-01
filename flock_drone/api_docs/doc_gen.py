"""API Doc generator for the drone side API."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

import os
import sys
import json
from flock_drone.settings import HYDRUS_SERVER_URL
from hydra_python_core.doc_writer import HydraDoc, HydraClass, HydraClassProp, HydraClassOp


def doc_gen(API, BASE_URL):
    """Generate API Doc for drone."""
    # Main API Doc
    api_doc = HydraDoc(API,
                       "API Doc for the drone side API",
                       "API Documentation for the drone side system",
                       API,
                       BASE_URL)

    # State Class
    # NOTE: Each drone will have only one State Class, this can't be deleted. Only read and update.
    state = HydraClass("State", "State", "Class for drone state objects")
    # Properties
    state.add_supported_prop(HydraClassProp(
        "http://auto.schema.org/speed", "Speed", True, False, False))
    state.add_supported_prop(HydraClassProp(
        "http://schema.org/geo", "Position", True, False, False))
    state.add_supported_prop(HydraClassProp(
        "http://schema.org/Property", "Direction", True, False, False))
    state.add_supported_prop(HydraClassProp(
        "http://schema.org/fuelCapacity", "Battery", True, True, False))
    state.add_supported_prop(HydraClassProp(
        "https://schema.org/status", "Status", True, False, False))

    # Drone Class
    # NOTE: The actual changes to the drone are to be made at the /api/Drone URI.
    # GET will return current State. POST will update the State.
    drone = HydraClass("Drone", "Drone", "Class for a drone", endpoint=True)
    # Properties
    drone.add_supported_prop(HydraClassProp(
        "vocab:State", "State", False, False, True))
    drone.add_supported_prop(HydraClassProp(
        "http://schema.org/name", "name", False, False, True))
    drone.add_supported_prop(HydraClassProp(
        "http://schema.org/model", "model", False, False, True))
    drone.add_supported_prop(HydraClassProp(
        "http://auto.schema.org/speed", "MaxSpeed", False, False, True))
    drone.add_supported_prop(HydraClassProp(
        "http://schema.org/device", "Sensor", False, False, True))
    drone.add_supported_prop(HydraClassProp(
        "http://schema.org/identifier", "DroneID", False, False, True))
    # Operations
    drone.add_supported_op(HydraClassOp("GetDrone",
                                        "GET",
                                        None,
                                        "vocab:Drone",
                                        [{"statusCode": 404, "description": "Drone not found"},
                                         {"statusCode": 200, "description": "Drone returned"}]))
    # When new commands are issued, mechanics will need to change the state of the drone
    drone.add_supported_op(HydraClassOp("UpdateDrone",
                                        "POST",
                                        "vocab:Drone",
                                        None,
                                        [{"statusCode": 200, "description": "Drone updated"}]))
    drone.add_supported_op(HydraClassOp("AddDrone",
                                        "PUT",
                                        "vocab:Drone",
                                        None,
                                        [{"statusCode": 200, "description": "Drone added"}]))

    # Command Class
    # NOTE: Commands are stored in a collection. You may GET a command or you may DELETE it, there is not UPDATE.
    command = HydraClass("Command", "Command", "Class for drone commands")
    command.add_supported_prop(HydraClassProp(
        "http://schema.org/identifier", "DroneID", False, False, True))
    command.add_supported_prop(HydraClassProp(
        "vocab:State", "State", False, False, True))
    # Used by mechanics to get newly added commands
    command.add_supported_op(HydraClassOp("GetCommand",
                                          "GET",
                                          None,
                                          "vocab:Command",
                                          [{"statusCode": 404, "description": "Command not found"},
                                           {"statusCode": 200, "description": "Command Returned"}]))
    # Used by server to add new commands
    command.add_supported_op(HydraClassOp("AddCommand",
                                          "PUT",
                                          "vocab:Command",
                                          None,
                                          [{"statusCode": 201, "description": "Command added"}]))
    # Used by mechanics to delete command after it has been executed
    command.add_supported_op(HydraClassOp("DeleteCommand",
                                          "DELETE",
                                          None,
                                          None,
                                          [{"statusCode": 200, "description": "Command deleted"}]))

    # Datastream class
    # NOTE: This is for the Datastream to be captured/generated. The mechanics module will enter random data and POST it.
    # The server will read[GET] the data when it needs it. No need for collections. Only one instance showing current reading of sensor
    # The URI is /api/Datastream
    datastream = HydraClass("Datastream", "Datastream",
                            "Class for a data entry from drone sensors", endpoint=True)
    datastream.add_supported_prop(HydraClassProp(
        "http://schema.org/QuantitativeValue", "Temperature", False, False, True))
    datastream.add_supported_prop(HydraClassProp(
        "http://schema.org/identifier", "DroneID", False, False, True))
    datastream.add_supported_prop(HydraClassProp(
        "http://schema.org/geo", "Position", False, False, True))
    datastream.add_supported_op(HydraClassOp("GetDatastream",
                                             "GET",
                                             None,
                                             "vocab:Datastream",
                                             [{"statusCode": 404, "description": "Datastream not found"},
                                              {"statusCode": 200, "description": "Datastream returned"}]))
    datastream.add_supported_op(HydraClassOp("UpdateDatastream",
                                             "POST",
                                             "vocab:Datastream",
                                             None,
                                             [{"statusCode": 200, "description": "Datastream updated"}]))
    datastream.add_supported_op(HydraClassOp("AddDatastream",
                                             "PUT",
                                             "vocab:Datastream",
                                             None,
                                             [{"statusCode": 200, "description": "Datastream added"}]))

    anomaly = HydraClass(
        "Anomaly", "Anomaly", "Class for Temperature anomalies that need to be confirmed", endpoint=True)
    anomaly.add_supported_prop(HydraClassProp(
        "vocab:Location", "Location", False, False, True))
    anomaly.add_supported_prop(HydraClassProp(
        "http://schema.org/identifier", "DroneID", False, False, True))
    # Status of any anomaly can be ["Positive", "Negative", "Confirming"]
    anomaly.add_supported_prop(HydraClassProp(
        "http://schema.org/eventStatus", "Status", False, False, True))
    anomaly.add_supported_prop(HydraClassProp(
        "http://schema.org/identifier", "AnomalyID", False, False, True))
    anomaly.add_supported_op(HydraClassOp("GetAnomaly",
                                          "GET",
                                          None,
                                          "vocab:Anomaly",
                                          [{"statusCode": 404, "description": "Anomaly not found"},
                                           {"statusCode": 200, "description": "Anomaly returned"}]))
    anomaly.add_supported_op(HydraClassOp("AddAnomaly",
                                          "PUT",
                                          "vocab:Anomaly",
                                          None,
                                          [{"statusCode": 201, "description": "Anomaly added successfully"}]))
    anomaly.add_supported_op(HydraClassOp("UpdateAnomaly",
                                          "POST",
                                          "vocab:Anomaly",
                                          None,
                                          [{"statusCode": 201, "description": "Anomaly updated successfully"}]))

    api_doc.add_supported_class(state, collection=False)
    api_doc.add_supported_class(drone, collection=False)
    api_doc.add_supported_class(command, collection=True)
    api_doc.add_supported_class(datastream, collection=False)
    api_doc.add_supported_class(anomaly, collection=False)

    api_doc.add_baseCollection()
    api_doc.add_baseResource()
    api_doc.gen_EntryPoint()
    return api_doc


if __name__ == "__main__":
    dump = json.dumps(doc_gen("api", HYDRUS_SERVER_URL).generate(),
                      indent=4, sort_keys=True)
    doc = '''"""\nGenerated API Documentation for Server API using server_doc_gen.py."""\n\ndoc = %s''' % dump
    doc = doc + '\n'
    doc = doc.replace('true', '"true"')
    doc = doc.replace('false', '"false"')
    doc = doc.replace('null', '"null"')
    f = open(os.path.join(os.path.dirname(__file__), "doc.py"), "w")
    f.write(doc)
    f.close()
