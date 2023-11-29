from agent import *
from model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer
import os


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0

    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 1
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0

    if isinstance(agent, Car):
        portrayal["Color"] = "blue"  # Puedes cambiar el color a tu elección
        portrayal["Layer"] = 2
        portrayal["w"] = 0.25
        portrayal["h"] = 0.25

    return portrayal


width = 0
height = 0

dir_path = os.path.dirname(__file__)
city_base_path = os.path.join(dir_path, '../city_files/2022_base.txt')

with open(city_base_path) as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"N": 5}

print(width, height)
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

server = ModularServer(CityModel, [grid], "Traffic Base", model_params)

server.port = 8521  # The default
server.launch()
