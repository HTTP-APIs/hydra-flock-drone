"""Operation related to Drone state POST operations."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

from flock_drone.mechanics.main import get_drone, update_drone


def gen_State(drone_id, battery, direction, position, status, speed):
    """Generate a State objects."""
    state = {
        "@type": "State",
        "DroneID": drone_id,
        "Battery": battery,
        "Direction": direction,
        "Position": position,
        "Status": status,
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
        drone["State"] = state
        update_drone(drone)
        print("Drone state updated successfully.")
    else:
        print("ERROR: DroneID %s not valid." % (state["DroneID"]))


def get_state():
    """Get the current drone state from the drone server."""
    drone = get_drone()
    drone_state = drone["State"]
    drone_state["DroneID"] = drone["DroneID"]

    return drone_state
