"""Distance related functions."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

from haversine import haversine
import math

earth_radius = 6371.0   # For Kilometers


def change_in_latitude(distance):
    """Given a distance north, return the change in latitude."""
    return math.degrees((distance / earth_radius))


def change_in_longitude(latitude, distance):
    """Given a latitude and a distance west, return the change in longitude."""
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius * math.cos(math.radians(latitude))
    return math.degrees((distance / r))


def convert_direction_to_north_or_west(distance_moved, direction):
    """Convert East and South direction to North and East."""
    if direction in ["S", "E"]:
        if direction == "S":
            distance_moved = distance_moved * -1
            direction = "N"
        elif direction == "E":
            distance_moved = distance_moved * -1
            direction = "W"

    return distance_moved, direction


def gen_new_coordinates_from_change_in_coordinates(old_coordinates, change_in_coordinates):
    """Calculate new coordinates given coordinates(lat,lon) and change_in_coordinates(lat,lon)."""
    return tuple(map(lambda x, y: x + y, old_coordinates, change_in_coordinates))


def get_new_coordinates(old_coordinates, distance_moved, direction):
    """Get new coordinates given old coordinates (lat,lon), distance moved, direction of movement."""
    # Convert directions if needed
    distance_moved, direction = convert_direction_to_north_or_west(
        distance_moved, direction)

    if direction == "N":
        latitude_change = change_in_latitude(distance_moved)
        change_in_coordinates = (latitude_change, 0)

    elif direction == "W":
        latitude = old_coordinates[0]
        longitude_change = change_in_longitude(latitude, distance_moved)
        change_in_coordinates = (0, longitude_change)
    else:
        raise TypeError(
            "Not a valid direction of movement! Please use one of  ['N', 'S', 'E', 'W']")

    return gen_new_coordinates_from_change_in_coordinates(old_coordinates, change_in_coordinates)


def gen_square_path(coordinates, square_dimension):
    """Generate square path for area of interest."""
    path = list()
    path.append(get_new_coordinates(get_new_coordinates(
        coordinates, square_dimension, "W"), square_dimension, "S"))
    path.append(get_new_coordinates(get_new_coordinates(
        coordinates, square_dimension, "W"), square_dimension, "N"))
    path.append(get_new_coordinates(get_new_coordinates(
        coordinates, square_dimension, "E"), square_dimension, "N"))
    path.append(get_new_coordinates(get_new_coordinates(
        coordinates, square_dimension, "E"), square_dimension, "S"))

    return path


def gen_pos_limits_from_square_path(square_path):
    """Generate position bounds for drones."""
    return ([square_path[0][0], square_path[1][0]], [square_path[1][1], square_path[2][1]])


def get_distance_between_coordinates(a, b):
    """Get the distance between two sets of coordinates."""
    return haversine(a, b)


def deg2num(lat_deg, lon_deg, zoom = 12):
    """Convert latitute and longitude to map tile index."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) +
                                (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def get_direction(source, destination):
    """Find the direction drone needs to move to get from src to dest."""
    lat_diff = abs(source[0] - destination[0])
    long_diff = abs(source[1] - destination[1])
    if lat_diff > long_diff:
        if source[0] > destination[0]:
            return "S"
        else:
            return "N"
    else:
        if source[1] > destination[1]:
            return "E"
        else:
            return "W"


def is_valid_location(location, bounds):
    """Check if location is in drone bounds."""
    if min(bounds[0]) <= location[0] <= max(bounds[0]):
        if min(bounds[1]) <= location[1] <= max(bounds[1]):
            return True
    return False


def calculate_drone_range(speed, loop_time=15):
    """Calculate the range of drone for each iteration given speed in km/h and loop time in sec."""
    drone_range = float(speed) * (float(loop_time) / 3600) * (1 / 2)
    return drone_range


def drone_reached_destination(drone, destination):
    """Check if the drone has reached its destination."""
    drone_position = tuple(float(a)
                           for a in drone["DroneState"]["Position"].split(","))
    drone_range = calculate_drone_range(drone["DroneState"]["Speed"])

    # Generate a square bound for destination location
    bounds_square_path = gen_square_path(destination, drone_range)
    # Generate bounds for location
    destination_bounds = gen_pos_limits_from_square_path(bounds_square_path)

    if is_valid_location(drone_position, destination_bounds):
        return True
    return False


if __name__ == "__main__":
    a = (-30.040397656836609, -30.03373871559225)
    print("Initial Coordinates", a)
    b = get_new_coordinates(a, 1, "N")
    print("Final Coordinates", b)
    distance_between_coordinates = get_distance_between_coordinates(a, b)
    print("Distance_between_coordinates", distance_between_coordinates)
    print("\n\n")
    print(deg2num(-10.040397656836609, -55.03373871559225, 13))

    print(gen_pos_limits_from_square_path(gen_square_path(a, 10)))
