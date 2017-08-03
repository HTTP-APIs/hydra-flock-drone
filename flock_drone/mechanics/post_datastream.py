"""Operation related to datastream post operations."""
import os, sys
curDir = os.path.dirname(__file__)
parentDir = os.path.abspath(os.path.join(curDir,os.pardir)) # this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir,os.pardir)) # this will return parent directory.
sys.path.insert(0, superParentDir)

from flock_drone.mechanics.main import RES_CS, RES_DRONE
from flock_drone.mechanics.main import CENTRAL_SERVER, DRONE
from flock_drone.mechanics.main import get_datastream
from hydra import SCHEMA, Resource


def send_datastream(datastream):
    """Post the drone current datastream to the central server."""
    post_datastream = RES_CS.find_suitable_operation(SCHEMA.AddAction, CENTRAL_SERVER.Datastream)
    resp, body = post_datastream(datastream)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    new_datastream = Resource.from_iri(resp['location'])
    print("Datastream posted successfully.")
    return new_datastream

if __name__ == "__main__":
    datastream = get_datastream()
    print(datastream)
    print(send_datastream(datastream))
