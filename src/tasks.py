import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import sys
import math

from config import SetupConfiguration
from utils import fixed_sum_random


# random.seed(1404)
# Tasks temporary
_T = random.choice(SetupConfiguration.T_CHOICES)
_n = random.randint(*SetupConfiguration.NODES_RANGE)
_p = SetupConfiguration.P

# Resources
_nr = random.randint(*SetupConfiguration.RESOURCES_RANGE)
_total_access = [random.choice(SetupConfiguration.RESOURCE_ACCESS_CHOICES) for _ in range(_nr)]

print(f"Number of nodes: {_n}, resource types: {_nr}, accesses: {_total_access}")

G = nx.DiGraph()
G.graph["T"] = _T

for i in range(_n):
    # Add custom attrs
    G.add_node(i, label=f"Node {i}", color='lightblue', size=100)

# Generate graph
for i in range(_n):
    for j in range(i + 1, _n): # To make sure no loop occur
        if random.random() < _p:
            # Configure edge
            G.add_edge(i, j, weight=0.1)


def uunifast(n, total_utilization):
    """Generate n random utilizations summing to total_utilization."""
    utilizations = []
    sum_u = total_utilization
    for i in range(1, n):
        next_sum = sum_u * np.random.random() ** (1 / (n - i))
        utilizations.append(sum_u - next_sum)
        sum_u = next_sum
    utilizations.append(sum_u)
    return utilizations

def allocate_resourses(n, total_access):
    if sum(total_access) < n:
        print("Not enough resources!")
        sys.exit(0)
        
    resources = [t for t, count in enumerate(total_access) for _ in range(count)]
    random.shuffle(resources)

    split_indices = sorted(random.sample(range(1, len(resources)), n - 1))
    split_indices = [0] + split_indices + [len(resources)]

    tasks = [resources[split_indices[i]:split_indices[i+1]] for i in range(n)]
    return tasks

total_utilization = 0.8
node_utilizations = uunifast(_n, total_utilization)
resources = allocate_resourses(_n, _total_access)
for node, u, r in zip(G.nodes(), node_utilizations, resources):
    G.nodes[node]["u"] = u
    computation_time = int(G.graph["T"] * u)
    G.nodes[node]["c"] = computation_time
    G.nodes[node]["resources"] = r
    critical_c = fixed_sum_random(len(r), math.ceil(computation_time * 0.6))
    normal_c = fixed_sum_random(len(r) + 1, math.floor(computation_time * 0.4))
    times, parts = [], []
    for i in range(2 * len(r) + 1):
        if i % 2: 
            times.append(critical_c[i//2])
            parts.append(r[i//2])
        else:
            times.append(normal_c[i//2])
            parts.append(-1)
            
    G.nodes[node]["times"] = times
    G.nodes[node]["parts"] = parts
    print(G.nodes[node])


def critical_path_dag(G):
    """Find the longest path (in nodes) in a DAG."""
    topo_order = list(nx.topological_sort(G))
    
    dist = {node: -1 for node in G.nodes()}
    predecessor = {node: None for node in G.nodes()}
    
    dist[topo_order[0]] = 1  # Path length = 1 (only itself)
    
    for node in topo_order:
        for neighbor in G.successors(node):
            if dist[neighbor] < dist[node] + 1:
                dist[neighbor] = dist[node] + 1
                predecessor[neighbor] = node
    
    max_node = max(dist, key=dist.get)
    max_length = dist[max_node]
    
    path = []
    current = max_node
    while current is not None:
        path.append(current)
        current = predecessor[current]
    path.reverse()
    
    return path, max_length

# Add source/sink
root_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
leaf_nodes = [node for node in G.nodes() if G.out_degree(node) == 0]

G.add_node("Source", label="Source", color='green', size=100, u=0, c=0)  # Custom attributes
G.add_node("Sink", label="Sink", color='red', size=100, u=0, c=0)
for root in root_nodes:
    G.add_edge("Source", root)
for leaf in leaf_nodes:
    G.add_edge(leaf, "Sink")

G.graph["C"] = sum([G.nodes[i]["c"] for i in G.nodes()])
G.graph["critical_path"], _ = critical_path_dag(G)
print(G.graph["critical_path"])

pos = nx.spring_layout(G)

node_labels = nx.get_node_attributes(G, 'label')
node_colors = [G.nodes[i]['color'] for i in G.nodes()]
node_sizes = [G.nodes[i]['size'] for i in G.nodes()]

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15, width=1.5)
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

plt.title("Directed Erdős–Rényi Graph (n=10, p=0.3)")
plt.axis('off')
# plt.show()
