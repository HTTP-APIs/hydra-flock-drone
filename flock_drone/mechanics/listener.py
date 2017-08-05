import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

import threading
import json
from flock_drone.mechanics.manage_commands import get_command_collection
from flock_drone.mechanics.main import get_drone, update_drone
from flock_drone.mechanics.distance import get_new_coordinates, gen_square_path, gen_drone_pos_limits
from flock_drone.mechanics.main import update_drone_at_controller
from flock_drone.mechanics.main import gen_Datastream, update_datastream
from flock_drone.mechanics.post_datastream import send_datastream
from flock_drone.mechanics.main import gen_DroneLog, gen_HttpApiLog, get_controller_location
from flock_drone.mechanics.post_logs import send_dronelog, send_http_api_log
import random, math

## Drone main Loop time settings
global LOOP_TIME
LOOP_TIME = 15

CONTROLLER_LOC = tuple(float(x) for x in get_controller_location().split(","))

DRONE_BOUNDS = gen_drone_pos_limits(gen_square_path(CONTROLLER_LOC, 10))


## Battery related functions
def discharge_drone_battery(drone):
    """Handle drone battery discharging."""
    battery_level = drone["DroneState"]["Battery"]
    if(int(battery_level) > 3):
        drone["DroneState"]["Battery"] = int(drone["DroneState"]["Battery"])-1
    else:
        # Battery level critical change drone status to OFF
        drone["DroneState"]["Status"] = "Off"

    return drone

def charge_drone_battery(drone):
    """Handle the drone battery charging operration."""
    battery_level = drone["DroneState"]["Battery"]
    if int(battery_level) < 95:
        ## Increase battery level
        drone["DroneState"]["Battery"] = int(battery_level) + 5
    else:
        ## If battery >= 95 set battery level to 100%
        drone["DroneState"]["Battery"] = 100
    return drone

def is_drone_charging(drone):
    """Check if the drone status is charging."""
    return drone["DroneState"]["Status"] == "Charging"

def drone_is_not_off(drone):
    """Check if drone status is not off."""
    return drone["DroneState"]["Status"] != "Off"


def handle_drone_battery(drone):
    """Handle the drone battery status."""
    if drone_is_not_off(drone):
        if is_drone_charging(drone):
            drone = charge_drone_battery(drone)
        else:
            drone = discharge_drone_battery(drone)
    return drone



## Distance related functions

def is_valid_location(location, bounds):
    """Check if location is in drone bounds."""
    if min(bounds[0]) <= location[0] <= max(bounds[0]):
        if min(bounds[1]) <= location[1] <= max(bounds[1]):
            return True
    return False

def get_random_direction_for_drone():
    """Return a random direction for drone."""
    return random.choice(["N", "S", "E", "W"])


def handle_invalid_pos(drone, distance_travelled):
    """Handle invalid position update for drone."""
    direction = get_random_direction_for_drone()
    drone["DroneState"]["Direction"] = direction

    drone_position = tuple(float(a) for a in drone["DroneState"]["Position"].split(","))
    new_drone_position = get_new_coordinates(drone_position, distance_travelled, direction)
    if is_valid_location(new_drone_position, DRONE_BOUNDS):
        drone["DroneState"]["Position"] = ",".join(map(str, new_drone_position))
        return drone
    else:
        return handle_invalid_pos(drone, distance_travelled)



def calculate_dis_travelled(speed, time):
    """Calculate the distance travelled(in Km) in a give amount of time(s)"""
    return (speed*time)/3600.0

def update_drone_position(drone, distance_travelled, direction):
    """Update the drone position given the distance travelled and direction of travel."""
    drone_position = tuple(float(a) for a in drone["DroneState"]["Position"].split(","))
    new_drone_position = get_new_coordinates(drone_position, distance_travelled, direction)
    if is_valid_location(new_drone_position, DRONE_BOUNDS):
        drone["DroneState"]["Position"] = ",".join(map(str, new_drone_position))
    else:
        drone = handle_invalid_pos(drone, distance_travelled)
    return drone

def handle_drone_position(drone):
    """Handle the drone position changes."""
    drone_speed = float(drone["DroneState"]["Speed"])
    distance_travelled = calculate_dis_travelled(drone_speed, LOOP_TIME)

    drone_direction = str(drone["DroneState"]["Direction"])

    drone = update_drone_position(drone, distance_travelled, drone_direction)

    return drone



## Datastream related functions
def gen_random_sensor_data():
    """Generate random sensor data for drone datastream."""
    drone_sensor_options = ["Normal", "Critical", "High"]
    return random.choice(drone_sensor_options)




def main():
    """ The main 15 second time loop for drone."""
    drone = get_drone()

    ## handle the drone battery change
    drone_identifier = drone["DroneID"]
    drone = handle_drone_battery(drone)
    drone_battery = drone["DroneState"]["Battery"]
    drone_direction = drone["DroneState"]["Direction"]

    ## Handle drone position change
    drone = handle_drone_position(drone)

    if(drone["DroneState"]["Direction"] != drone_direction):
        ## Generate and send DroneLog
        dronelog = gen_DroneLog("Drone %s" %(str(drone_identifier),), "changed direction to %s" %(str(drone["DroneState"]["Direction"])))
        send_dronelog(dronelog)
        ## Generate and send HttpApiLog
        http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"PUT DroneLog", "Controller")
        send_http_api_log(http_api_log)

    ## Update the drone at central contoller.

    ## Send Drone battery and Http Api logs
    if int(drone_battery == 20):
        ## Generate and send DroneLog
        dronelog = gen_DroneLog("Drone %s" %(str(drone_identifier),), "battery Low %s" %(str(drone["DroneState"]["Battery"])))
        send_dronelog(dronelog)
        ## Generate and send HttpApiLog
        http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"PUT DroneLog", "Controller")
        send_http_api_log(http_api_log)

    elif int(drone_battery == 4):
        ## Generate and send DroneLog
        dronelog = gen_DroneLog("Drone %s" %(str(drone_identifier)), "Battery level critical, will shutdown soon!")
        send_dronelog(dronelog)
        ## Generate and send HttpApiLog
        http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"PUT DroneLog", "Controller")
        send_http_api_log(http_api_log)


    if int(drone_identifier) != -1000:
        update_drone_at_controller(drone, drone_identifier)
        ## Generate and send HttpApiLog
        http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"POST Drone", "Controller")
        send_http_api_log(http_api_log)
    ## update the drone locally
    update_drone(drone)
    ## Generate and send HttpApiLog
    http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"POST DroneState", "Localhost")
    send_http_api_log(http_api_log)



    ## Handle sensor datastream
    datastream = gen_Datastream(gen_random_sensor_data(), drone["DroneState"]["Position"], drone_identifier)
    if int(drone_identifier != -1000):
        send_datastream(datastream)
        ## Generate and send HttpApiLog
        http_api_log = gen_HttpApiLog("Drone %s" %(str(drone_identifier)),"PUT Datastream", "Controller")
        send_http_api_log(http_api_log)
    update_datastream(datastream)

    # call main() again in 60 LOOP_TIME
    threading.Timer(LOOP_TIME, main).start()

if __name__ == "__main__":
    main()
