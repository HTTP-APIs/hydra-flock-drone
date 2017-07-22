import os

## Using sqlite as database
global DB_URL
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
DB_URL = 'sqlite:///{}'.format(db_path)


global HYDRUS_SERVER_URL, API_NAME, PORT
HYDRUS_SERVER_URL = "http://localhost:8081/"
PORT = 8081
API_NAME = "droneapi"

## Drone configuration
global CENTRAL_SERVER_NAMESPACE, DRONE1_NAMESPACE
CENTRAL_SERVER_NAMESPACE = "http://localhost:8080/serverapi/vocab#"
DRONE_NAMESPACE = "http://localhost:8081/droneapi/vocab#"

global DRONE_URL, CENTRAL_SERVER_URL
DRONE_URL = "http://localhost:8081"
CENTRAL_SERVER_URL = "http://localhost:8080"

global IRI_CS, IRI_DRONE
IRI_CS = "http://localhost:8080/serverapi"
IRI_DRONE = "http://localhost:8081/droneapi"
