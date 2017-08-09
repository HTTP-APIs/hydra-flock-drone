"""Handle operations related to new commands for the drone."""
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
    get_command_collection_ = RES_DRONE.find_suitable_operation(None, None, DRONE.CommandCollection)
    resp, body = get_command_collection_()
    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)

    body = json.loads(body.decode('utf-8'))
    command_list = list()
    for command in body["members"]:
        regex = r'/(.*)/(\d)'
        matchObj = re.match(regex, command["@id"])
        if matchObj:
            command_list.append(get_command(matchObj.group(2)))

    return command_list


def add_command(command):
    """Add command to drone server."""
    add_command_ = RES_DRONE.find_suitable_operation(SCHEMA.AddAction, DRONE.Command)
    resp, body = add_command_(command)

    assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
    new_command = Resource.from_iri(resp['location'])
    print("Command posted successfully.")
    return new_command


def get_command(id_):
    """Get the command using @id."""
    try:
        i = Resource.from_iri(DRONE_URL + "/api/CommandCollection/" + str(id_))
        # name = i.value(SCHEMA.name)
        resp, body = i.find_suitable_operation(operation_type=None, input_type=None,
                                               output_type=DRONE.Command)()
        assert resp.status in [200, 201], "%s %s" % (resp.status, resp.reason)
        body = json.loads(body.decode('utf-8'))
        body.pop("@context")
        body.pop("@type")
        return body
    except:
        return {404: "Resource with Id %s not found!" % (id_,)}


def delete_command(id_):
    """Delete a command from the collection given command @id attribute."""
    try:
        i = Resource.from_iri(DRONE_URL + "/api/CommandCollection/" + id_)
        # name = i.value(SCHEMA.name)
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


if __name__ == "__main__":
    print(get_command_collection())
    # state = gen_State(-1000, "50", "North", "1,1", "Active", 100)
    # command = gen_Command(123, state)
    # print(add_command(command))
    # print(delete_command("/api/CommandCollection/175"))
