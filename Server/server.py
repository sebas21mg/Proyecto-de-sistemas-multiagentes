# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023 

from flask import Flask, request, jsonify
from agents.model import RandomModel
from agents.agent import Car, ObstacleAgent

# Size of the board:
randomModel = None
currentStep = 0

# This application will be used to interact with Unity
app = Flask("Traffic example")

# This route will be used to send the parameters of the simulation to the server.
# The servers expects a POST request with the parameters in a form.
@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, randomModel

    if request.method == 'POST':
        currentStep = 0

        print(request.form)

        # Create the model using the parameters sent by Unity
        randomModel = RandomModel()

        # Return a message to Unity saying that the model was created successfully
        return jsonify({"message":"Parameters recieved, model initiated."})

# This route will be used to get the positions of the agents
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the agents and return them to Unity in JSON format.
        # Note that the positions are sent as a list of dictionaries, where each dictionary has the id and position of an agent.
        # The y coordinate is set to 1, since the agents are in a 3D world. The z coordinate corresponds to the row (y coordinate) of the grid in mesa.

        agentPositions = []
        for agents, (x, z) in randomModel.grid.coord_iter():
            for agent in agents:
                if (isinstance(agent, Car)):
                    agentPositions.append({"id": str(agent.unique_id), "x": x, "y":0.5, "z":z})

        return jsonify({'positions':agentPositions})


# This route will be used to get the positions of the obstacles
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        # Get the positions of the obstacles and return them to Unity in JSON format.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.

        obstaclesPositions = []
        for agents, (x, z) in randomModel.grid.coord_iter():
            for agent in agents:
                if (isinstance(agent, ObstacleAgent)):
                    obstaclesPositions.append({"id": str(agent.unique_id), "x": x, "y":1, "z":z})

        return jsonify({'positions':obstaclesPositions})

# This route will be used to update the model
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        # Update the model and return a message to Unity saying that the model was updated successfully
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})


if __name__=='__main__':
    # Run the flask server in port 8585
    app.run(host="localhost", port=8585, debug=True)
