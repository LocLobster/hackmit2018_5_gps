import code
import requests
#import json
from collections import defaultdict
from sets import Set

USERNAME = 'LocLobster_ef2bd6'
MAP_REQUEST = 'https://gps.hackmirror.icu/api/map?user='+str(USERNAME)
TIME_REQUEST = 'https://gps.hackmirror.icu/api/time?user='+str(USERNAME)
POS_REQUEST = 'https://gps.hackmirror.icu/api/position?user='+str(USERNAME)
PROBABILITY_REQUEST = 'https://gps.hackmirror.icu/api/probability?user='+str(USERNAME)

POST_UP     =  'https://gps.hackmirror.icu/api/move?user='+str(USERNAME)+'&move=up'
POST_DOWN   =  'https://gps.hackmirror.icu/api/move?user='+str(USERNAME)+'&move=down'
POST_LEFT   =  'https://gps.hackmirror.icu/api/move?user='+str(USERNAME)+'&move=left'
POST_RIGHT  =  'https://gps.hackmirror.icu/api/move?user='+str(USERNAME)+'&move=right'

POST_RESET = 'https://gps.hackmirror.icu/api/reset?user='+str(USERNAME)

WIDTH = 150
DESTINATION = 22499
#r = requests.post(POST_RESET)
#print r.text

class Graph:
  def __init__(self):
    self.nodes = set()
    self.edges = defaultdict(list)
    self.distances = {}

  def add_node(self, value):
    self.nodes.add(value)

  #def add_edge(self, from_node, to_node, distance):
  def add_edge(self, to_node, from_node, distance):
    self.edges[from_node].append(to_node)
    #self.edges[to_node].append(from_node)
    self.distances[(from_node, to_node)] = distance


def dijsktra(graph, initial):
  visited = {initial: 0}
  path = {}

  nodes = set(graph.nodes)

  while nodes:
    min_node = None
    for node in nodes:
      if node in visited:
        if min_node is None:
          min_node = node
        elif visited[node] < visited[min_node]:
          min_node = node

    if min_node is None:
      break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
      weight = current_weight + graph.distances[(min_node, edge)]
      if edge not in visited or weight < visited[edge]:
        visited[edge] = weight
        path[edge] = min_node

  return visited, path


def get_path():
    r = requests.get(MAP_REQUEST)
    graph_json  = r.json()

    graph = Graph()

    num_nodes = len(graph_json['graph'])
    for i in range(num_nodes):
        graph.add_node(i)

    for i in range(num_nodes):
        for j in range(len(graph_json['graph'][i])):
            graph.add_edge(i,graph_json['graph'][i][j],1)


    visited, path = dijsktra(graph, DESTINATION )
    print "Num nodes connected to endpont " + str(len(visited))

    # Find nodes that are dead ends
    dead_nodes = []
    for i in range(num_nodes):
        if i not in visited.keys():
            dead_nodes.append(i)
    print "Num nodes that are dead ends  " + str(len(dead_nodes))

    penalized_graph = graph
    penalty = 9.001
    # Add a penalty for nodes connected to dead ends
    danger_edges = Set()
    for dead_node in dead_nodes:
        for danger_node in penalized_graph.edges[dead_node]:
            for penalty_edge in penalized_graph.edges[danger_node]:
                graph.distances[(danger_node, penalty_edge)] += penalty

    penalized_visited, penalized_path = dijsktra(penalized_graph, DESTINATION)

    return penalized_visited, penalized_path, penalized_graph


def get_current_node():
    r = requests.get(POS_REQUEST)
    pos_json  = r.json()
    print pos_json

    return pos_json['row']*WIDTH + pos_json['col']

def handle_move(current_node, next_node):
    if next_node == current_node - 1:        # Move left
        r = requests.post(POST_LEFT)
    elif next_node == current_node + 1:      # Move right
        r = requests.post(POST_RIGHT)
    elif next_node == current_node - WIDTH:  # Move up
        r = requests.post(POST_UP)
    elif next_node == current_node + WIDTH:  # Move down
        r = requests.post(POST_DOWN)
    else:
        return False  # something went wrong
    return True


num_success = 0
num_fail    = 0
for iteration in range(100):
    print 'ITERATION ' + str(iteration)
    r = requests.post(POST_RESET)
    visited, path, graph = get_path()

    current_node = 0
    for i in range(600):
        current_node = get_current_node()
        print 'Current Node ' + str(current_node)
        if current_node == DESTINATION:
            print 'done!'
            break

        if current_node not in path:
            print 'we stuck'
            break

        next_node = path[current_node]

        handle_move(current_node, next_node)

    if current_node != DESTINATION:
        num_fail += 1
        print 'need to reset'
    else:
        num_success += 1
        break


print "Num_success = "+str(num_success)
print "Num_fail= "+str(num_fail)
code.interact(local=locals())

