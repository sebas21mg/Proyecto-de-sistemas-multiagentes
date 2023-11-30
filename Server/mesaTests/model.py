from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import random
import os
import networkx as nx
import matplotlib.pyplot as plt

class CityModel(Model):
    """ 
    Crea un modelo basado en un mapa de ciudad.

    Args:
        N: Número de agentes en la simulación
    """

    def __init__(self):

        dir_path = os.path.dirname(__file__)

        map_dictionary_path = os.path.join(dir_path, '../city_files/mapDictionary.json')
        city_base_path = os.path.join(dir_path, '../city_files/2023_base.txt')

        # Cargar el diccionario del mapa. El diccionario mapea los caracteres en el archivo del mapa con el agente correspondiente.
        self.map_data = json.load(open(map_dictionary_path))
        self.traffic_lights = []
        self.destinations = []
        self.step_count = 0
        self.city_graph = nx.DiGraph()
        self.car_counter = 0 
        self.load_city_map(city_base_path)
        self.add_cars()

        self.running = True
        self.create_city_graph()

    def load_city_map(self, city_base_path):
        """
        Carga el mapa de la ciudad desde un archivo.

        Args:
            city_base_path (str): Ruta al archivo del mapa de la ciudad.
        """
        with open(city_base_path) as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    self.create_agent(r, c, col)

    def create_agent(self, r, c, col):
        """
        Crea un agente según el carácter en la posición dada del mapa.

        Args:
            r (int): Fila en el mapa.
            c (int): Columna en el mapa.
            col (str): Carácter que representa el tipo de agente en la posición (r, c).
        """
        if col in ["v", "^", ">", "<", "L", "Q", "A", "F"]:
            road_agent = Road(f"road_{r*self.width+c}", self, self.map_data[col])
            self.grid.place_agent(road_agent, (c, self.height - r - 1))
            self.city_graph.add_node((c, self.height - r - 1), type='road')

        elif col in ["S", "s"]:
            traffic_light_agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(self.map_data[col]))
            self.grid.place_agent(traffic_light_agent, (c, self.height - r - 1))
            self.schedule.add(traffic_light_agent)
            self.traffic_lights.append(traffic_light_agent)
            self.city_graph.add_node((c, self.height - r - 1), type='traffic_light')

        elif col == "#":
            obstacle_agent = Obstacle(f"ob_{r*self.width+c}", self)
            self.grid.place_agent(obstacle_agent, (c, self.height - r - 1))

        elif col == "D":
            destination_agent = Destination(f"dest_{r*self.width+c}", self)
            self.grid.place_agent(destination_agent, (c, self.height - r - 1))
            self.destinations.append(destination_agent.pos)
            self.city_graph.add_node((c, self.height - r - 1), type='destination')

    def add_cars(self):
        """
        Agrega coches en las esquinas del mapa con destinos aleatorios.
        """
        corners = [
            (0, 0),
            (0, self.height - 1),
            (self.width - 1, 0),
            (self.width - 1, self.height - 1)
        ]
        

        for corner in corners:
            x, y = corner
            
            # Check if the position is available
            if self.is_position_available(x, y):
                # Once a position is available, add the car
                destination = random.choice(self.destinations)
                road_direction = self.get_road_direction(x, y)
                car_agent = Car(f"car_{self.step_count}_{x}_{y}", self, destination)
                car_agent.direction = road_direction
                self.grid.place_agent(car_agent, (x, y))
                self.schedule.add(car_agent)
                
                # Incrementar el contador de carros
                self.car_counter += 1
    
    def get_road_direction(self, x, y):
        """
        Obtiene la dirección del camino en la posición dada.

        Args:
            x (int): Coordenada x del camino.
            y (int): Coordenada y del camino.

        Returns:
            str: Dirección del camino ('Up', 'Down', 'Left', 'Right').
        """
        possible_roads = self.grid.get_neighbors((x, y), moore=True, include_center=True, radius=1)
        for road in possible_roads:
            if isinstance(road, Road):
                return road.direction

        return "Undefined"
    
    def is_position_available(self, x, y):
        """
        Verifica si la posición dada en el mapa está disponible.

        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.

        Returns:
            bool: True si la posición está disponible, False de lo contrario.
        """
        return self.validPosition(x, y) and not any(isinstance(agent, Car) for agent in self.grid.get_cell_list_contents((x, y)))

    def validPosition(self, x, y):
        """
        Verifica si la posición dada en el mapa es válida.

        Args:
            x (int): Coordenada x.
            y (int): Coordenada y.

        Returns:
            bool: True si la posición es válida, False de lo contrario.
        """
        return 0 <= x < self.width and 0 <= y < self.height and (
            any(isinstance(agent, (Road, Traffic_Light, Destination)) for agent in self.grid.get_cell_list_contents((x, y)))
        )

    def add_traffic_light_edges(self, x, y, directions):
        """
        Agrega bordes al grafo de la ciudad para los semáforos en la posición dada.

        Args:
            x (int): Coordenada x del semáforo.
            y (int): Coordenada y del semáforo.
            directions (dict): Direcciones permitidas desde el semáforo.
        """
        for direction_name, (dx, dy) in directions.items():
            adjacent_x, adjacent_y = x + dx, y + dy
            if self.validPosition(adjacent_x, adjacent_y) and any(isinstance(agent, Road) for agent in self.grid.get_cell_list_contents((adjacent_x, adjacent_y))):
                adjacent_agents = self.grid.get_cell_list_contents((adjacent_x, adjacent_y))
                road_agent = next((agent for agent in adjacent_agents if isinstance(agent, Road)), None)
                if road_agent:
                    if self.aligning_directions(road_agent, x, y, adjacent_x, adjacent_y):
                        self.city_graph.add_edge((adjacent_x, adjacent_y), (x, y), weight=self.calculate_edge_weight(adjacent_x, adjacent_y, x, y))
                    else:
                        self.city_graph.add_edge((x, y), (adjacent_x, adjacent_y), weight=self.calculate_edge_weight(x, y, adjacent_x, adjacent_y))
                        
    def aligning_directions(self, road_agent, tl_x, tl_y, road_x, road_y):
        """
        Verifica si el semáforo y la carretera están alineados en la misma dirección.

        Args:
            road_agent: Agente de la carretera.
            tl_x (int): Coordenada x del semáforo.
            tl_y (int): Coordenada y del semáforo.
            road_x (int): Coordenada x de la carretera.
            road_y (int): Coordenada y de la carretera.

        Returns:
            bool: True si están alineados, False de lo contrario.
        """
        if road_agent.direction == "Up" and road_y < tl_y:
            return True
        if road_agent.direction == "Down" and road_y > tl_y:
            return True
        if road_agent.direction == "Left" and road_x > tl_x:
            return True
        if road_agent.direction == "Right" and road_x < tl_x:
            return True
        return False

    def calculate_edge_weight(self, x, y, nx, ny):
        base_weight = 1
        next_agents = self.grid.get_cell_list_contents((nx, ny))
        if any(isinstance(agent, Traffic_Light) and agent.state for agent in next_agents):
            return base_weight * 5
        return base_weight
    
    def create_city_graph(self):
        """
        Crea el grafo de la ciudad con nodos y bordes.
        """
        directions = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        diagonal_directions = {
            'Right': [('Right', 'Up'), ('Right', 'Down')],
            'Up': [('Up', 'Right'), ('Up', 'Left')],
            'Left': [('Left', 'Up'), ('Left', 'Down')],
            'Down': [('Down', 'Right'), ('Down', 'Left')]
        }

        for x in range(self.width):
            for y in range(self.height):
                agents = self.grid.get_cell_list_contents((x, y))
                if any(isinstance(agent, Destination) for agent in agents):
                    self.destination_edges(x, y, directions)
                elif any(isinstance(agent, Road) for agent in agents):
                    road_agent = next((agent for agent in agents if isinstance(agent, Road)), None)
                    if road_agent:
                        self.road_edges(x, y, road_agent, directions, diagonal_directions)
                elif any(isinstance(agent, Traffic_Light) for agent in agents):
                    self.add_traffic_light_edges(x, y, directions)
    
    def destination_edges(self, x, y, directions):
        """
        Agrega bordes al grafo de la ciudad para las destinos en la posición dada.

        Args:
            x (int): Coordenada x del destino.
            y (int): Coordenada y del destino.
            directions (dict): Direcciones permitidas desde el destino.
        """
        for direction in directions.values():
            dx, dy = direction
            nx, ny = x + dx, y + dy
            if self.validPosition(nx, ny) and any(isinstance(agent, Road) for agent in self.grid.get_cell_list_contents((nx, ny))):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.city_graph.add_edge((nx, ny), (x, y), weight=weight)

    def road_edges(self, x, y, road_agent, directions, diagonal_directions):
        road_directions = road_agent.direction if isinstance(road_agent.direction, list) else [road_agent.direction]
        for direction in road_directions:
            dx, dy = directions[direction]
            nx, ny = x + dx, y + dy
            if self.validPosition(nx, ny) and not any(isinstance(agent, Traffic_Light) for agent in self.grid.get_cell_list_contents((nx, ny))):
                weight = self.calculate_edge_weight(x, y, nx, ny)
                self.city_graph.add_edge((x, y), (nx, ny), weight=weight)
                if direction in diagonal_directions:
                    for diag in diagonal_directions[direction]:
                        ddx, ddy = (directions[diag[0]][0] + directions[diag[1]][0], directions[diag[0]][1] + directions[diag[1]][1])
                        nnx, nny = x + ddx, y + ddy
                        if self.validPosition(nnx, nny) and not any(isinstance(agent, Traffic_Light) for agent in self.grid.get_cell_list_contents((nnx, nny))):
                            self.city_graph.add_edge((x, y), (nnx, nny), weight=weight * 1.5)
                            
    def remove_car(self, car):
        self.schedule.remove(car)
        self.grid.remove_agent(car)
        
        # Decrementar el contador de carros
        self.car_counter -= 1
    
    def weightEdges(self, x, y, nx, ny):
        """
        Calcula el peso de un borde entre dos posiciones en el mapa.

        Args:
            x (int): Coordenada x de la posición inicial.
            y (int): Coordenada y de la posición inicial.
            nx (int): Coordenada x de la posición final.
            ny (int): Coordenada y de la posición final.

        Returns:
            int: Peso del borde.
        """
        base_weight = 1
        next_agents = self.grid.get_cell_list_contents((nx, ny))
        if any(isinstance(agent, Traffic_Light) and agent.state == "on" for agent in next_agents):
            return base_weight * 10
        return base_weight

    def step(self):
        """
        Avanza un paso en la simulación.
        """
        self.schedule.step()
        self.step_count += 1
        print(self.car_counter)
        if self.step_count % 1 == 0:
            self.add_cars()

