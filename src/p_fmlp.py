import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
import math
from copy import deepcopy

from config import SetupConfiguration
from utils import fixed_sum_random_int, fixed_sum_random_float, uunifast


# random.seed(1404)
rq = []

class Task():
    def __init__(self, id, utilization, total_access):
        self.id = id
        self.T = random.choice(SetupConfiguration.T_CHOICES)
        self.n = random.randint(*SetupConfiguration.NODES_RANGE)
        self.p = SetupConfiguration.P
        self.utilization = utilization
        self.total_access = total_access

        print(f"Task {id}: Number of nodes: {self.n}, T: {self.T}")

        self.G = nx.DiGraph()
        self.generate_graph()        
        
    def generate_graph(self):
        for i in range(self.n):
            # Add custom attrs
            self.G.add_node(i, label=f"Node {i}", color='lightblue', size=100, executing=False, priority=self.T)

        # Generate graph
        for i in range(self.n):
            for j in range(i + 1, self.n): # To make sure no loop occur
                if random.random() < self.p:
                    # Configure edge
                    self.G.add_edge(i, j, weight=0.1)
                    
        # Add source/sink
        root_nodes = [node for node in self.G.nodes() if self.G.in_degree(node) == 0]
        leaf_nodes = [node for node in self.G.nodes() if self.G.out_degree(node) == 0]

        self.G.add_node("Source", label="Source", color='green', size=100, u=0, c=0)
        self.G.add_node("Sink", label="Sink", color='red', size=100, u=0, c=0)
        for root in root_nodes:
            self.G.add_edge("Source", root)
        for leaf in leaf_nodes:
            self.G.add_edge(leaf, "Sink")


    def set_utilization(self):
        node_utilizations = uunifast(self.n, self.utilization)
        for node, u in zip(self.G.nodes(), node_utilizations):
            self.G.nodes[node]["u"] = u
            self.G.nodes[node]["c"] = int(self.T * u)
    
    
    def allocate_resourses(self):
        resources = [t for t, count in enumerate(self.total_access) for _ in range(count)]
        random.shuffle(resources)
        
        if sum(self.total_access) < self.n:
            allocations = [[] for _ in range(self.n)]
            for r in resources:
                allocations[random.randint(0, self.n - 1)].append(r)
        else: 
            split_indices = sorted(random.sample(range(1, len(resources)), self.n - 1))
            split_indices = [0] + split_indices + [len(resources)]
            allocations = [resources[split_indices[i]:split_indices[i+1]] for i in range(self.n)]

        for node, r in zip(self.G.nodes(), allocations):
            this_node = self.G.nodes[node]
            this_node["resources"] = r
            if len(r) > 0:
                critical_c = fixed_sum_random_int(len(r), math.ceil(this_node["c"] * 0.6))
                normal_c = fixed_sum_random_int(len(r) + 1, math.floor(this_node["c"] * 0.4))
            else:
                critical_c = []
                normal_c = [this_node["c"]]
            times, parts = [], []
            for i in range(2 * len(r) + 1):
                if i % 2: 
                    times.append(critical_c[i//2])
                    parts.append(r[i//2])
                else:
                    times.append(normal_c[i//2])
                    parts.append(-1)
                    
            this_node["times"] = times
            this_node["parts"] = parts
            
    
    def critical_path_dag(self):
        """Find the longest path (in nodes) in a DAG."""
        topo_order = list(nx.topological_sort(self.G))
        
        dist = {node: -1 for node in self.G.nodes()}
        predecessor = {node: None for node in self.G.nodes()}
        
        dist[topo_order[0]] = 1  # Path length = 1 (only itself)
        
        for node in topo_order:
            for neighbor in self.G.successors(node):
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
    
    
    def show_graph(self):
        pos = nx.spring_layout(self.G)

        node_labels = nx.get_node_attributes(self.G, 'label')
        node_colors = [self.G.nodes[i]['color'] for i in self.G.nodes()]
        node_sizes = [self.G.nodes[i]['size'] for i in self.G.nodes()]

        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_size=node_sizes)
        nx.draw_networkx_edges(self.G, pos, arrowstyle='->', arrowsize=15, width=1.5)
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=10)

        plt.title("Directed Erdős–Rényi Graph (n=10, p=0.3)")
        plt.axis('off')
        plt.show()
  
  
def select_task(tasks, i):
    for task in tasks:
        if task.G.number_of_nodes() == 1:
            tasks.remove(task)
    if i >= len(tasks):
        return None
    return sorted(tasks, key=lambda x: x.T)[i]

def get_runnaable_node(task, resource_status):
    task.G.remove_nodes_from(["Source"])
    root_nodes = [node for node in task.G.nodes() if (task.G.in_degree(node) == 0 
                                                      and node not in ["Sink"]
                                                      and task.G.nodes[node]["executing"] == False)]
    removable = []
    for node in root_nodes:
        while len(task.G.nodes[node]["times"]) > 0 and task.G.nodes[node]["times"][0] == 0:
            task.G.nodes[node]["times"].pop(0)
            task.G.nodes[node]["parts"].pop(0) 
        if len(task.G.nodes[node]["parts"]) == 0:
            removable.append(node) 
            continue  
        if task.G.nodes[node]["parts"][0] == -1 or resource_status[task.G.nodes[node]["parts"][0]] == 1:
            task.G.remove_nodes_from(removable)
            return node, task.G.nodes[node]
        elif resource_status[task.G.nodes[node]["parts"][0]] == 0:
            rq[task.G.nodes[node]["parts"][0]].append((task, node, task.G.nodes[node]))

    task.G.remove_nodes_from(removable)
    return None, None
    
  
def schedule(tasks: list[Task], nr, n_cpus):
    running_tasks = deepcopy(tasks)
    resource_status = [1 for _ in range(nr)]
    hyperperiod = math.lcm(*[task.T for task in tasks]) # type: ignore

    time = 0
    executing = [None for _ in range(n_cpus)]
    while time < hyperperiod:
        for cpu in range(n_cpus):
            if executing[cpu] is None:
                node_name = None
                k = 0
                while node_name is None and k < len(running_tasks):
                    to_run = select_task(running_tasks, k)
                    if to_run is None:
                        break
                    node_name, node = get_runnaable_node(to_run, resource_status)
                    k += 1
                if node_name is None:
                    continue
                
                executing[cpu] = (to_run, node_name, node)
                node["executing"] = True
                
            if executing[cpu] is not None:
                
                k = 0
                node_name = None
                while node_name is None and k < len(running_tasks):
                    to_run = select_task(running_tasks, k)
                    if to_run is None:
                        break
                    node_name, node = get_runnaable_node(to_run, resource_status)
                    # print(node_name, node, k)
                    k += 1
                if node_name is not None and to_run.T < executing[cpu][0].T and executing[cpu][2]["parts"][0] == -1: # Preemption
                    executing[cpu][2]["executing"] = 0
                    executing[cpu] = (to_run, node_name, node)
                    node["executing"] = True
                
                to_run, node_name, node = executing[cpu]
                print(f"time: {time}, cpu: {cpu}, id: {to_run.id}, node_name: {node_name}, node: {node}")

                node["times"][0] -= 1
                if node["times"][0] == 0:
                    node["executing"] = False
                    ridx = node["parts"][0]
                    node["times"].pop(0)
                    node["parts"].pop(0)
                    executing[cpu] = None
                    if len(node["parts"]) == 0:
                        to_run.G.remove_node(node_name)
                        if to_run.G.number_of_nodes() == 1:
                            running_tasks.remove(to_run) 
                    if len(rq[ridx]) > 0:
                        executing[cpu] = rq[ridx][0]
                        rq[ridx].pop(0)
        for task in tasks:
            if time % task.T == 0:
                for i in running_tasks:
                    if time > 0 and i.id == task.id:
                        print(f"task {i.id} missed deadline at {time}")
                        sys.exit(1)
                running_tasks.append(deepcopy(task))           
        time += 1

        

if __name__ == "__main__":  
    n_cpus = random.randint(*SetupConfiguration.CPU_CHOICES)
    n_tasks = random.randint(n_cpus//2, n_cpus)

    print(f"Number of CPUs: {n_cpus}, Number of Tasks: {n_tasks}")

    # Resources
    nr = random.randint(*SetupConfiguration.RESOURCES_RANGE)
    rq = [[] for _ in range(nr)]
    total_access = [random.choice(SetupConfiguration.RESOURCE_ACCESS_CHOICES) for _ in range(nr)]
    task_accesses = []
    for i in range(nr):
        task_accesses.append(fixed_sum_random_int(n_tasks, total_access[i]))
    transposed_task_accesses = [list(row) for row in zip(*task_accesses)]
    
    utilizations = fixed_sum_random_float(n_cpus, SetupConfiguration.U_norm * n_cpus)

    tasks = []

    for i in range(n_tasks):
        t = Task(i, utilizations[i], transposed_task_accesses[i])

        # t1.show_graph()
        t.set_utilization()
        t.allocate_resourses()
        tasks.append(t)

        print(f"Critical Path for task {i}: ", t.critical_path_dag())
    
    schedule(tasks, nr, n_cpus)
