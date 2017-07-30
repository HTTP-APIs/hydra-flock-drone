"""Handle main configuration for the drone."""
from hydra import Resource, SCHEMA
from rdflib import Namespace
import json
import os
from flock_drone.settings import CENTRAL_SERVER_NAMESPACE, DRONE_NAMESPACE
from flock_drone.settings import DRONE_URL, CENTRAL_SERVER_URL
from flock_drone.settings import IRI_CS, IRI_DRONE

global CENTRAL_SERVER, DRONE1, DRONE_URL
CENTRAL_SERVER = Namespace(CENTRAL_SERVER_NAMESPACE)
# print(CENTRAL_SERVER)
DRONE1 = Namespace(DRONE_NAMESPACE)
# print(DRONE1)

global RES_CS, RES_DRONE
RES_CS = Resource.from_iri(IRI_CS)
RES_DRONE = Resource.from_iri(IRI_DRONE)


# Drone related methods
def get_drone_default():
    """Return a default drone object with DroneID -1 for initialization."""
    drone_default = {
        "@type": "Drone",
        "DroneID": -1000,
        "name": "Drone 1",
        "model": "xyz",
        "MaxSpeed": 50,
        "Sensor": "Temperature",
        "DroneState": {
            "@type": "State",
            "Speed": 0,
            "Position": "0,0",
            "Battery": 100,
            "Direction": "North",
            "SensorStatus": "Inactive",
        }
    }

    return drone_default


def get_drone():
    """Get the drone object from drone server."""
    get_drone_ = RES_DRONE.find_suitable_operation(
                 operation_type=None, input_type=None,
                 output_type=DRONE1.Drone)
    resp, body = get_drone_()
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    drone = json.loads(body.decode('utf-8'))
    drone.pop("@id", None)
    drone.pop("@context", None)
    return drone

def get_drone_id():
    """Return current drone id from drone server."""
    drone = get_drone()
    return int(drone["DroneID"])


def update_drone(drone):
    """Update the drone object on drone server."""
    update_drone_ = RES_DRONE.find_suitable_operation(
                    operation_type=SCHEMA.UpdateAction,
                    input_type=DRONE1.Drone)
    resp, body = update_drone_(drone)
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

    return Resource.from_iri(resp['location'])


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


def update_datastream(datastream):
    """Update the drone datastream on drone server."""
    update_datastream_ = RES_DRONE.find_suitable_operation(
        operation_type=SCHEMA.UpdateAction, input_type=DRONE1.Datastream)
    resp, body = update_datastream_(datastream)
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

    return Resource.from_iri(resp['location'])


def get_datastream():
    """Get the drone datastream from drone server."""
    get_datastream_ = RES_DRONE.find_suitable_operation(
        operation_type=None, input_type=None, output_type=DRONE1.Datastream)
    resp, body = get_datastream_()
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

    datastream = json.loads(body.decode('utf-8'))
    # remove extra contexts from datastream
    datastream.pop("@context", None)
    datastream.pop("@id", None)
    return datastream



# Status related methods
def gen_State(drone_id, battery, direction, position, sensor_status, speed):
    """Generate a State objects."""
    state = {
        "@type": "State",
        "DroneID": drone_id,
        "Battery": battery,
        "Direction": direction,
        "Position": position,
        "SensorStatus": sensor_status,
        "Speed": speed,
    }
    return state


def update_state(state):
    """Update the drone state on drone server."""
    drone = get_drone()
    if int(drone["DroneID"]) == state["DroneID"]:
        # Remove the DroneID key from state
        state.pop("DroneID", None)

        # Update the drone state
        drone["DroneState"] = state
        update_drone(drone)
        print("Drone state updated successfully.")
    else:
        print("ERROR: DroneID %s not valid." % (state["DroneID"]))



def get_state():
    """Get the current drone state from the drone server."""
    drone = get_drone()
    drone_state = drone["DroneState"]
    drone_state["DroneID"] = drone["DroneID"]

    return drone_state

# Command related methods


def gen_Command(drone_id, state):
    """Create a command entity."""
    command = {
        "@type": "Command",
        "DroneID": drone_id,
        "State": state
    }
    return command

if __name__ == "__main__":

    get_drone()
    print(update_drone(get_drone_default()))
    # print(get_drone_id())
    # datastream = gen_datastream(100, "0,0", get_drone_id())
    # print(update_datastream(datastream))
    # print(get_datastream())
    # state = gen_state(-1000, "50", "North", "1,1", "Active", 100)
    # print(state)
    # print(update_state(state))
    # print(get_state())
