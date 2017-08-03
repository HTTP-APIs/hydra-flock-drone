"""Initialize drone."""
from flock_drone.mechanics.main import RES_CS
from flock_drone.mechanics.main import CENTRAL_SERVER
from hydra import SCHEMA, Resource
from flock_drone.mechanics.main import get_drone, get_drone_default, update_drone, get_drone_position
from flock_drone.mechanics.main import gen_Datastream, update_datastream, get_drone_id, get_controller_location
from flock_drone.settings import CENTRAL_SERVER_URL


def init_drone_locally():
    """Initialize the drone locally with Negative identifier."""
    try:
        get_drone()
        print("Drone already initialized.")
    except Exception as e:
        print(e)
        drone = get_drone_default()
        location = get_controller_location()
        print(location)
        drone["DroneState"]["Position"] = location
        update_drone(drone)
        print("Drone initalized locally!")


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
        i = Resource.from_iri(CENTRAL_SERVER_URL + drone_id)
        resp, _ = i.find_suitable_operation(SCHEMA.DeleteAction, None)()
        if resp.status // 100 != 2:
            return "error deleting <%s>" % i.identifier
        else:
            return "successfully deleted <%s>" % i.identifier
    except Exception as e:
        print(e)
        return {404: "Resource with Id %s not found!" % (drone_id,)}


def update_drone_id(id_):
    """Update the drone identifier."""
    # GET current drone object
    drone = get_drone()
    # Update the drone id
    drone["DroneID"] = id_

    # Update drone object
    update_drone(drone)
    print("DroneID updated successfully with id ", id_)
    return None


def init_drone():
    """Initialize drone."""
    # Add drone to the central_server and get identifier
    init_drone_locally()

    drone = get_drone()
    drone_id = drone.pop("DroneID", None)
    ## If drone has default negative id initialize else remove old drone and then inintialize.
    if int(drone_id) == -1000:
        drone_id = int(add_drone(drone))
    else:
        ## Remove old drone
        res = remove_drone("/api/DroneCollection/"+drone_id)
        print("Previous drone successfully deleted from the central server.")
        drone_id = int(add_drone(drone))

    # Update the drone on localhost
    update_drone_id(drone_id)

    print("Drone initialized successfully!")
    return None


def init_datastream_locally():
    """Initialize the datasteam locally."""
    datastream = gen_Datastream("Normal", get_drone_position(), get_drone_id())
    update_datastream(datastream)
    print("Datastream initialized locally")
    return None


if __name__ == "__main__":
    init_drone()
    init_datastream_locally()
