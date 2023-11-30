# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023

from flask import Flask, request, jsonify
from agents.model import CityModel
from agents.agent import *

# Size of the board:
randomModel = None
currentStep = 0

# This application will be used to interact with Unity
app = Flask("Traffic example")

# This route will be used to send the parameters of the simulation to the server.
# The servers expects a POST request with the parameters in a form.


@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, randomModel, modelCells

    if request.method == 'POST':
        currentStep = 0

        print(request.form)

        # Create the model using the parameters sent by Unity
        randomModel = CityModel()

        # Return a message to Unity saying that the model was created successfully
        return jsonify({"message": "Parameters recieved, model initiated."})

# This route will be used to get the positions of the agents


@app.route('/getCars', methods=['GET'])
def getCars():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the agents and return them to Unity in JSON format.
        # Note that the positions are sent as a list of dictionaries, where each dictionary has the id and position of an agent.
        # The y coordinate is set to 1, since the agents are in a 3D world. The z coordinate corresponds to the row (y coordinate) of the grid in mesa.

        carsPos = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z - 1, "destX": agent.destination[0], "destZ": agent.destination[1] - 1} for agents, (x, z)
                   in randomModel.grid.coord_iter() for agent in agents if isinstance(agent, Car)]

        return jsonify({'positions': carsPos})


# This route will be used to get the positions of the obstacles
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the obstacles and return them to Unity in JSON format.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.

        obstaclesPos = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z - 1} for agents, (x, z)
                        in randomModel.grid.coord_iter() for agent in agents if isinstance(agent, Obstacle)]

        return jsonify({'positions': obstaclesPos})

# This route will be used to get the positions of the obstacles


@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the obstacles and return them to Unity in JSON format.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.

        trafficLightsPos = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z - 1, "state": agent.state} for agents, (x, z)
                            in randomModel.grid.coord_iter() for agent in agents if isinstance(agent, Traffic_Light)]

        return jsonify({'positions': trafficLightsPos})

# This route will be used to get the positions of the obstacles


@app.route('/getRoad', methods=['GET'])
def getRoad():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the obstacles and return them to Unity in JSON format.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.

        roadPos = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z - 1} for agents, (x, z)
                   in randomModel.grid.coord_iter() for agent in agents if isinstance(agent, Road)]

        return jsonify({'positions': roadPos})

# This route will be used to get the positions of the obstacles


@app.route('/getDestination', methods=['GET'])
def getDestination():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the obstacles and return them to Unity in JSON format.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.

        destinationPos = [{"id": str(agent.unique_id), "x": x, "y": 1, "z": z - 1} for agents, (x, z)
                          in randomModel.grid.coord_iter() for agent in agents if isinstance(agent, Destination)]

        return jsonify({'positions': destinationPos})

# This route will be used to update the model


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        # Update the model and return a message to Unity saying that the model was updated successfully
        randomModel.step()
        currentStep += 1
        return jsonify({'message': f'Model updated to step {currentStep}.', 'currentStep': currentStep})


if __name__ == '__main__':
    # Run the flask server in port 8585
    app.run(host="localhost", port=8585, debug=True)
