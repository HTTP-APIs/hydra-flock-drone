"""Initialize drone."""
import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

from flock_drone.mechanics.main import CENTRAL_SERVER, RES_CS, RES_DRONE, DRONE
from hydra import SCHEMA, Resource
from flock_drone.mechanics.main import get_drone, get_drone_default, update_drone, get_controller_location, update_drone_at_controller
from flock_drone.mechanics.datastream import gen_Datastream, add_datastream
from flock_drone.settings import CENTRAL_SERVER_URL


def init_drone_locally():
    """Initialize the drone locally with Negative identifier."""
    drone = get_drone_default()
    location = get_controller_location()["Location"]
    print(location)
    drone["DroneState"]["Position"] = location
    add_drone_locally(drone)
    print("Drone initalized locally!")


def add_drone_locally(drone):
    """Add the drone object to the central server and return Id."""
    try:
        add_drone_ = RES_DRONE.find_suitable_operation(
            SCHEMA.AddAction, DRONE.Drone)
        resp, body = add_drone_(drone)
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        drone_id = resp['location'].split("/")[-1]
        print(drone_id)
        return drone_id
    except (ConnectionRefusedError, KeyError) as e:
        print(e)
        print("Connection Refused, Please check the central controller.")
        print("Using default id instead")
        return -1000


def add_drone(drone):
    """Add the drone object to the central server and return Id."""
    try:
        add_drone_ = RES_CS.find_suitable_operation(
            SCHEMA.AddAction, CENTRAL_SERVER.Drone)
        resp, body = add_drone_(drone)
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        drone_id = resp['location'].split("/")[-1]
        print(drone_id)
        return drone_id
    except (ConnectionRefusedError, KeyError) as e:
        print(e)
        print("Connection Refused, Please check the central controller.")
        print("Using default id instead")
        return -1000


def remove_drone(drone_id):
    """Remove previous drone object from the central server."""
    try:
        i = Resource.from_iri(CENTRAL_SERVER_URL + "/api/DroneCollection" + drone_id)
        resp, _ = i.find_suitable_operation(SCHEMA.DeleteAction, None)()
        if resp.status // 100 != 2:
            return "error deleting <%s>" % i.identifier
        else:
            return "successfully deleted <%s>" % i.identifier
    except Exception as e:
        print(e)
        return {404: "Resource with Id %s not found!" % (drone_id,)}


def init_drone():
    """Initialize drone."""
    # Add drone to the central_server and get identifier
    init_drone_locally()

    drone = get_drone()
    drone_id = drone["DroneID"]
    # If drone has default negative id initialize else remove old drone and then inintialize.
    if int(drone_id) == -1000:
        drone_id = int(add_drone(drone))
    else:
        # Remove old drone
        remove_drone(drone_id)
        print("Previous drone successfully deleted from the central server.")
        drone_id = int(add_drone(drone))
    print(drone_id)
    # Update the drone on localhost
    drone["DroneID"] = drone_id

    update_drone(drone)
    update_drone_at_controller(drone, drone_id)

    print("Drone initialized successfully!")


def init_datastream_locally():
    """Initialize the datasteam locally."""
    drone = get_drone()
    id_ = drone["DroneID"]
    position = drone["DroneState"]["Position"]
    datastream = gen_Datastream("0", position, id_)
    add_datastream(datastream)
    print("Datastream initialized locally")


if __name__ == "__main__":
    init_drone()
    init_datastream_locally()
