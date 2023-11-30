from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from .agent import Car, Obstacle, Road, Traffic_Light, Destination
import random
import os
import json


class CityModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """

    def __init__(self):

        self.traffic_lights = []
        self.destinations = []
        self.step_count = 0
        self.grid = None
        self.schedule = None

        self.create_city()
        self.add_corner_cars()
        self.running = True

    def create_city(self):
        dir_path = os.path.dirname(__file__)

        map_dictionary_path = os.path.join(
            dir_path, '../city_files/mapDictionary.json')
        city_base_path = os.path.join(dir_path, '../city_files/2022_base.txt')

        map_dictionary = json.load(open(map_dictionary_path))

        with open(city_base_path) as baseFile:
            lines = baseFile.readlines()
            # Obtener las dimensiones de la simulación
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<", "L", "Q", "A", "F"]:
                        agent = Road(f"r_{r*self.width+c}",
                                     self, map_dictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            f"tl_{r*self.width+c}", self, False if col == "S" else True, int(map_dictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                        roadAgent = Road(f"r_{r*self.width+c}", self)
                        self.grid.place_agent(
                            roadAgent, (c, self.height - r - 1))

                    if col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destinations.append(agent.pos)

    def add_corner_cars(self):
        corners = [
            (0, 0),
            (0, 1),
            (0, self.height - 1),
            (1, self.height - 1),
            (self.width - 1, 0),
            (self.width - 2, 1),
            (self.width - 1, self.height - 1),
            (self.width - 2, self.height - 2)
        ]

        for corner in corners:
            x, y = corner
            destination = random.choice(self.destinations)
            agent = Car(f"car_{self.step_count}_{x}_{y}", self, destination)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1

        if self.step_count % 10 == 0:
            self.add_corner_cars()
