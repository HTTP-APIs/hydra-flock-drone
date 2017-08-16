"""Tests for checking if all the drone endpoints are working properly."""
import os
import sys
curDir = os.path.dirname(__file__)
# this will return parent directory.
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
# this will return parent directory.
superParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.insert(0, superParentDir)

import unittest
import requests
import json
from flock_drone.mechanics.main import get_drone_default
from flock_drone.mechanics.main import gen_Command, gen_State, gen_Datastream, ordered


DRONE_URL = "http://localhost:8081/"


class TestDroneRequests(unittest.TestCase):
    """Test for drone endpoints."""

    def test_request_vocab(self):
        """Test the drone vocab."""
        request_get = requests.get(DRONE_URL + 'api/vocab')
        request_put = requests.put(
            DRONE_URL + 'api/vocab', data=json.dumps(dict(foo='bar')))
        request_post = requests.post(
            DRONE_URL + 'api/vocab', data=json.dumps(dict(foo='bar')))
        request_delete = requests.delete(DRONE_URL + 'api/vocab')
        assert request_get.status_code == 200
        assert request_put.status_code == 405
        assert request_post.status_code == 405
        assert request_delete.status_code == 405

    def test_request_entrypoint(self):
        """Test the drone entrypoint."""
        request_get = requests.get(DRONE_URL + 'api/')
        request_put = requests.put(
            DRONE_URL + 'api/', data=json.dumps(dict(foo='bar')))
        request_post = requests.post(
            DRONE_URL + 'api/', data=json.dumps(dict(foo='bar')))
        request_delete = requests.delete(DRONE_URL + 'api/')
        assert request_get.status_code == 200
        assert request_put.status_code == 405
        assert request_post.status_code == 405
        assert request_delete.status_code == 405

    def test_request_drone(self):
        """Test the /Drone endpoint."""
        request_get = requests.get(DRONE_URL + 'api/Drone')
        request_put = requests.put(
            DRONE_URL + 'api/Drone', data=json.dumps(get_drone_default()))
        request_post = requests.post(
            DRONE_URL + 'api/Drone', data=json.dumps(get_drone_default()))
        request_delete = requests.delete(DRONE_URL + 'api/Drone')
        # 404 if drone is not initialized use mechanics.drone_init to initialize
        assert request_get.status_code in [200, 404]
        assert request_put.status_code == 405
        assert request_post.status_code in [200, 201]
        assert request_delete.status_code == 405

    def test_request_datastream(self):
        """Test the /Datastream endpoint."""
        datastream = gen_Datastream(100, "0,0", -1000)

        request_get = requests.get(DRONE_URL + 'api/Datastream')
        request_put = requests.put(
            DRONE_URL + 'api/Datastream', data=json.dumps(datastream))
        request_post = requests.post(
            DRONE_URL + 'api/Datastream', data=json.dumps(datastream))
        request_delete = requests.delete(DRONE_URL + 'api/Datastream')
        # 404 if drone is not initialized use mechanics.drone_init to initialize
        assert request_get.status_code in [200, 404]
        assert request_put.status_code == 405
        assert request_post.status_code in [200, 201]
        assert request_delete.status_code == 405

    def test_request_command_collection(self):
        """Test the /CommandCollection endpoint."""
        state = gen_State(-1000, "50", "North", "1,1", "Active", 100)
        command = gen_Command(123, state)

        request_get = requests.get(DRONE_URL + 'api/CommandCollection')
        request_put = requests.put(
            DRONE_URL + 'api/CommandCollection', data=json.dumps(command))
        request_post = requests.post(
            DRONE_URL + 'api/CommandCollection', data=json.dumps(command))
        request_delete = requests.delete(DRONE_URL + 'api/CommandCollection')
        assert request_get.status_code == 200
        assert request_put.status_code == 201
        assert request_post.status_code == 405
        assert request_delete.status_code == 405

    def test_request_command_collection_wrong_type_put(self):
        """Test the /CommandCollection endpoint PUT with wrong type object."""
        state = gen_State(-1000, "50", "North", "1,1", "Active", 100)
        command = gen_Command(123, state)
        command["@type"] = "Dummy"

        request_put = requests.put(
            DRONE_URL + 'api/CommandCollection', data=json.dumps(command))
        assert request_put.status_code == 400

    def test_drone_data(self):
        """Test if drone data submitted is same as drone received back."""
        drone = get_drone_default()
        request_post = requests.post(
            DRONE_URL + 'api/Drone', data=json.dumps(drone))

        request_get = requests.get(DRONE_URL + 'api/Drone')
        received_drone = request_get.json()
        received_drone.pop("@id", None)
        received_drone.pop("@context", None)
        assert ordered(drone) == ordered(received_drone)

    def test_datastream_data(self):
        """Test if datastream data submitted is same as datastream received back."""
        datastream = gen_Datastream("100", "0,0", "-1000")
        request_post = requests.post(
            DRONE_URL + 'api/Datastream', data=json.dumps(datastream))

        request_get = requests.get(DRONE_URL + 'api/Datastream')
        received_datastream = request_get.json()
        received_datastream.pop("@id", None)
        received_datastream.pop("@context", None)

        assert ordered(datastream) == ordered(received_datastream)


if __name__ == '__main__':
    message = """
    Running tests for the app. Checking if all responses are in proper order.
    NOTE: This doesn't ensure that data is entered or deleted in a proper manner.
    It only checks the format of the reponses.
    """
    print(message)
    unittest.main()
