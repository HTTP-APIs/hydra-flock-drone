from haversine import haversine
import math



# Distances are measured in miles/Kilometers.
# Longitudes and latitudes are measured in degrees.
# Earth is assumed to be perfectly spherical.

# earth_radius = 3960.0 ## For miles
earth_radius = 6371.0 ## For Kilometers

def change_in_latitude(distance):
    """Given a distance north, return the change in latitude."""
    return math.degrees((distance/earth_radius))

def change_in_longitude(latitude, distance):
    """Given a latitude and a distance west, return the change in longitude."""
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius*math.cos(math.radians(latitude))
    return math.degrees((distance/r))


# print(change_in_latitude(-1))
# print(change_in_longitude(a[0], -1))

def convert_direction_to_north_or_west(distance_moved, direction):
    """Convert East and South direction to North and East."""
    if direction in ["S","E"]:
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
    """ Get new coordinates given old coordinates (lat,lon), distance moved in kilometers
    direction of movement [N, S, E, W]."""

    ## Convert directions if needed
    distance_moved, direction = convert_direction_to_north_or_west(distance_moved, direction)

    if direction == "N":
        latitude_change = change_in_latitude(distance_moved)
        change_in_coordinates = (latitude_change, 0)

    elif direction == "W":
        latitude = old_coordinates[0]
        longitude_change = change_in_longitude(latitude, distance_moved)
        change_in_coordinates = (0, longitude_change)
    else:
        raise TypeError("Not a valid direction of movement! Please use one of  ['N', 'S', 'E', 'W']")

    return gen_new_coordinates_from_change_in_coordinates(old_coordinates, change_in_coordinates)




def get_distance_between_coordinates(a,b):
    """Get the distance between two sets of coordinates."""
    return haversine(a,b)

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)



if __name__ == "__main__":

    a = (-30.040397656836609, -30.03373871559225) ## (lat,lon)
    print("Initial Coordinates", a)
    b = get_new_coordinates(a, 500, "S")
    print("Final Coordinates", b)
    distance_between_coordinates = get_distance_between_coordinates(a,b)
    print("Distance_between_coordinates", distance_between_coordinates)
    print("\n\n")
    print(deg2num(-10.040397656836609, -55.03373871559225, 13))
