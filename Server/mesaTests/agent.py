from mesa import Agent
import random
import heapq
import networkx as nx

class Car(Agent):
    def __init__(self, unique_id, model, destination):
        super().__init__(unique_id, model)
        self.direction = "Undefined"
        self.destination = destination
        self.path = []  
        self.stopped = False  
        self.time_since_lane_change = 0
        self.lane_change_cooldown = 6

    def calculate_path(self):
        start = self.pos
        goal = self.destination
        city_graph = self.model.city_graph
        path = nx.astar_path(city_graph, start, goal)
        path.pop(0)
        return path

    def can_move(self, current_position, next_position):
        contents = self.model.grid.get_cell_list_contents([next_position])

        for content in contents:
            if isinstance(content, Traffic_Light) and not content.state:
                return False
            elif isinstance(content, Car):
                return False

        return True

    def is_at_destination(self, next_pos):
        return next_pos == self.destination

    def get_cell_in_front(self):
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        direction = self.get_direction()

        if direction:
            dx, dy = directions[direction]
            front_x, front_y = self.pos[0] + dx, self.pos[1] + dy
            return front_x, front_y

        return None
    
    def get_direction(self):
        if self.path:
            dx = self.path[0][0] - self.pos[0]
            dy = self.path[0][1] - self.pos[1]
            if dx == 1:
                return 'Right'
            elif dx == -1:
                return 'Left'
            elif dy == 1:
                return 'Up'
            elif dy == -1:
                return 'Down'
            
    def is_opposite_direction(self, pos):
        """
        Verifica si la dirección de la celda diagonal es opuesta a la dirección actual del coche.

        Args:
            pos (tuple): Coordenadas de la celda diagonal.

        Returns:
            bool: True si las direcciones son opuestas, False de lo contrario.
        """
        dx = pos[0] - self.pos[0]
        dy = pos[1] - self.pos[1]
        diagonal_direction = None

        if dx == 1:
            diagonal_direction = 'Right'
        elif dx == -1:
            diagonal_direction = 'Left'
        elif dy == 1:
            diagonal_direction = 'Up'
        elif dy == -1:
            diagonal_direction = 'Down'

        return diagonal_direction and self.direction and self.are_opposite_directions(self.direction, diagonal_direction)
    
    def are_opposite_directions(self, dir1, dir2):
        """
        Verifica si dos direcciones son opuestas.

        Args:
            dir1 (str): Primera dirección.
            dir2 (str): Segunda dirección.

        Returns:
            bool: True si son opuestas, False de lo contrario.
        """
        opposite_directions = {
            'Up': 'Down',
            'Down': 'Up',
            'Left': 'Right',
            'Right': 'Left'
        }
        return opposite_directions.get(dir1) == dir2
    
    def check_for_lane_change(self):
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        if self.direction:
            dx, dy = directions[self.direction]
            vision_range = 3  # Número de celdas hacia adelante que se considerarán
            front_cell = self.get_cell_in_front()

            if front_cell is not None:
                lane_change_step = front_cell
                if self.model.validPosition(*lane_change_step):
                    neighborhood_cells = self.model.grid.get_neighborhood(lane_change_step, moore=True, include_center=True)
                    num_cars_in_next_position = sum(isinstance(c, Car) for cell in neighborhood_cells for c in self.model.grid.get_cell_list_contents([cell]))
        
                    if num_cars_in_next_position >= vision_range and self.time_since_lane_change >= self.lane_change_cooldown:
                        self.execute_lane_change()
    
    def execute_lane_change(self):
        diagonal_positions = [(self.pos[0] + ddx, self.pos[1] + ddy) for ddx, ddy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]]
        valid_diagonal_positions = [(x, y) for x, y in diagonal_positions if self.model.validPosition(x, y)]
        
        # Filtrar celdas diagonales con direcciones compatibles
        valid_diagonal_positions = [
            pos for pos in valid_diagonal_positions 
            if not self.is_opposite_direction(pos)
            and not any(isinstance(agent, (Car, Destination)) for agent in self.model.grid.get_cell_list_contents([pos]))
        ]

        if valid_diagonal_positions:
            new_position = valid_diagonal_positions[0]
            self.model.grid.move_agent(self, new_position)
            self.recalculate_path(new_position, self.destination)
            self.stopped = False
            self.direction = self.get_direction()
            self.time_since_lane_change = 0
    
    def recalculate_path(self, start=None, destination=None):
        if start:
            self.pos = start
        if destination:
            self.destination = destination

        try:
            self.path = self.calculate_path()

        except nx.NetworkXNoPath:

            self.path = []
    
    def move(self):
        self.time_since_lane_change += 1
        self.check_for_lane_change()

        if not self.path:
            self.path = self.calculate_path()

        if self.path:
            next_position = self.path[0]

            if self.is_at_destination(next_position):
                self.model.remove_car(self)
            else:
                self.try_to_move(next_position)

                front_cell = self.get_cell_in_front()

                if front_cell is not None:
                    next_cell = self.model.grid.get_cell_list_contents([front_cell]) if self.model.validPosition(*front_cell) else []

                    if not self.can_move(self.pos, front_cell) or next_cell:
                        self.stopped = True

    def try_to_move(self, next_position):
        self.direction = self.get_direction()
        if self.can_move(self.pos, next_position):
            self.model.grid.move_agent(self, next_position)
            self.path.pop(0)
        else:
            self.stopped = True

    def step(self):
        self.move()


class Traffic_Light(Agent):
    def __init__(self, unique_id, model, state=False, timeToChange=10):
        super().__init__(unique_id, model)
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state


class Destination(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Obstacle(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Road(Agent):
    def __init__(self, unique_id, model, direction="TrafficLight"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
