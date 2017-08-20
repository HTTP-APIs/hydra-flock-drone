"""Handle operations related to new commands for the drone."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

import json
import re
from hydra import Resource, SCHEMA

from flock_drone.mechanics.main import DRONE, RES_DRONE
from flock_drone.settings import DRONE_URL


def gen_Command(drone_id, state):
    """Create a command entity."""
    command = {
        "@type": "Command",
        "DroneID": drone_id,
        "State": state
    }
    return command


def get_command_collection():
    """Get command collection from the drone server."""
    try:
        get_command_collection_ = RES_DRONE.find_suitable_operation(
            None, None, DRONE.CommandCollection)
        resp, body = get_command_collection_()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

        body = json.loads(body.decode('utf-8'))

        return body["members"]
    except Exception as e:
        print(e)
        return None


def add_command(command):
    """Add command to drone server."""
    try:
        add_command_ = RES_DRONE.find_suitable_operation(
            SCHEMA.AddAction, DRONE.Command)
        resp, body = add_command_(command)

        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        new_command = Resource.from_iri(resp['location'])
        print("Command posted successfully.")
        return new_command
    except Exception as e:
        print(e)
        return None


def get_command(id_):
    """Get the command using @id."""
    try:
        i = Resource.from_iri(DRONE_URL + "/api/CommandCollection/" + str(id_))

        resp, body = i.find_suitable_operation(operation_type=None, input_type=None,
                                               output_type=DRONE.Command)()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        body = json.loads(body.decode('utf-8'))
        body.pop("@context")
        body.pop("@type")
        return body
    except Exception as e:
        print(e)
        return None


def delete_command(id_):
    """Delete a command from the collection given command @id attribute."""
    try:
        i = Resource.from_iri(DRONE_URL + "/api/CommandCollection/" + id_)
        resp, _ = i.find_suitable_operation(SCHEMA.DeleteAction)()
        if resp.status // 100 != 2:
            return "error deleting <%s>" % i.identifier
        else:
            return "deleted <%s>" % i.identifier
    except:
        return {404: "Resource with Id %s not found!" % (id_,)}


def delete_commands(command_ids):
    """Delete a list of commands."""
    for id_ in command_ids:
        delete_command(id_)
