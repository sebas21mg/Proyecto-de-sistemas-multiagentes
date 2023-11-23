from mesa import Agent


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """

    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = "Undefined"

    # Obtener la posición del siguiente movimiento usando la dirección provista
    def get_next_move_pos(self, direction, x, y):
        if direction == "Up":
            return (x, y + 1)
        elif direction == "Down":
            return (x, y - 1)
        elif direction == "Left":
            return (x - 1, y)
        elif direction == "Right":
            return (x + 1, y)

    def next_move(self):
        x, y = self.pos

        # Lista con todos los agentes que estén en la celda del carro
        current_cell = self.model.grid.get_cell_list_contents([(x, y)])

        # Si hay un Road en la celda
        if any(isinstance(agent, Road) for agent in current_cell):
            road_agent = next(
                agent for agent in current_cell if isinstance(agent, Road))

            if road_agent.direction != "TrafficLight":
                self.direction = road_agent.direction
                return self.get_next_move_pos(self.direction, x, y)
            else:
                traffic_light_agent = next(
                    agent for agent in current_cell if isinstance(agent, Traffic_Light))

                if (traffic_light_agent.state):
                    return self.get_next_move_pos(self.direction, x, y)
                else:
                    return x, y

        return (x, y)

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        # Calculate the next move
        next_position = self.next_move()
        # print(f"Next move of {self.unique_id}: {next_position}")
        # Move the agent to the calculated next position
        self.model.grid.move_agent(self, next_position)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()


class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """

    def __init__(self, unique_id, model, state=False, timeToChange=10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state


class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """

    def __init__(self, unique_id, model, direction="TrafficLight"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)

        self.direction = direction

    def step(self):
        pass
