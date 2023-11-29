from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from .agent import Car, ObstacleAgent
import random

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, width, height):
        # Multigrid is a special type of grid where each cell can contain multiple agents.
        self.grid = SingleGrid(width, height, torus = False) 
        self.width = width
        self.height = height
        self.step_count = 0

        # RandomActivation is a scheduler that activates each agent once per step, in random order.
        self.schedule = RandomActivation(self)
        
        self.running = True 


        # a = Car(1000, self) 
        # self.schedule.add(a)

        # self.grid.place_agent(a, (1, 1))
        self.add_corner_cars()

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
            agent = Car(f"car_{self.step_count}_{x}_{y}", self)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (x, y))


    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.step_count += 1