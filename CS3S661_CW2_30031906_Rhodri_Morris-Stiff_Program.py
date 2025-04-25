#!/usr/bin/env python3
"""
Enhanced Distance Vector Routing Simulation with Better Logging and Output.
"""

import math
import time
from typing import Dict, Tuple, Union, List

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class Router:
    def __init__(self, router_id: Union[int, str], neighbors: Dict[Union[int, str], float]):
        if not isinstance(router_id, (int, str)):
            raise ValueError("router_id must be int or str.")
        for nid, cost in neighbors.items():
            if not isinstance(nid, (int, str)):
                raise ValueError("Neighbor IDs must be int or str.")
            if not (isinstance(cost, (int, float)) and cost >= 0):
                raise ValueError(f"Link cost to neighbor {nid} must be a non-negative number.")
        
        self.router_id = router_id
        self.neighbors = neighbors
        self.routing_table: Dict[Union[int, str], Tuple[float, Union[int, str, None]]] = {
            self.router_id: (0.0, None)
        }

    def get_distance(self, destination: Union[int, str]) -> float:
        return self.routing_table.get(destination, (math.inf, None))[0]

    def get_filtered_routing_table(self, for_neighbor_id: Union[int, str]) -> Dict[Union[int, str], Tuple[float, Union[int, str, None]]]:
        filtered_table = {}
        for dest, (dist, next_hop) in self.routing_table.items():
            if next_hop == for_neighbor_id:
                continue
            filtered_table[dest] = (dist, next_hop)
        return filtered_table

    def update_table_from_neighbor(self, neighbor_id: Union[int, str], neighbor_table: Dict[Union[int, str], Tuple[float, Union[int, str, None]]]) -> bool:
        updated = False
        cost_to_neighbor = self.neighbors.get(neighbor_id, math.inf)

        for dest, (neighbor_dist, _) in neighbor_table.items():
            if dest == self.router_id:
                continue
            new_dist = cost_to_neighbor + neighbor_dist
            current_dist, current_next_hop = self.routing_table.get(dest, (math.inf, None))

            if new_dist < current_dist:
                self.routing_table[dest] = (new_dist, neighbor_id)
                print(f"{GREEN}  [Router {self.router_id}] Route to {dest}: cost {current_dist} -> {new_dist}, via {neighbor_id}{RESET}")
                updated = True

        return updated

def run_distance_vector_simulation(
    routers: List[Router],
    max_iterations: int = 10,
    link_failure_iter: int = 3,
    fail_pair: Tuple[Union[int, str], Union[int, str]] = (1, 2),
    delay_per_iteration: float = 2.5
) -> None:
    for iteration in range(1, max_iterations + 1):
        print(f"\n=== Iteration {iteration} ===")
        updates_this_round = 0

        if link_failure_iter is not None and iteration == link_failure_iter:
            a_id, b_id = fail_pair
            router_a = next((r for r in routers if r.router_id == a_id), None)
            router_b = next((r for r in routers if r.router_id == b_id), None)

            if router_a and router_b and b_id in router_a.neighbors and a_id in router_b.neighbors:
                router_a.neighbors[b_id] = math.inf
                router_b.neighbors[a_id] = math.inf
                print(f"{YELLOW}\n!!! WARNING: Link failure simulated between Router {a_id} and Router {b_id} (link cost set to infinity) !!!{RESET}")

        all_filtered_tables = {}
        for router in routers:
            sender_id = router.router_id
            all_filtered_tables[sender_id] = {}
            for neighbor_id in router.neighbors:
                filtered_table = router.get_filtered_routing_table(for_neighbor_id=neighbor_id)
                all_filtered_tables[sender_id][neighbor_id] = filtered_table

        for sender_router in routers:
            sender_id = sender_router.router_id
            for neighbor_id in sender_router.neighbors:
                neighbor_router = next(r for r in routers if r.router_id == neighbor_id)
                table_to_send = all_filtered_tables[sender_id][neighbor_id]
                if neighbor_router.update_table_from_neighbor(sender_id, table_to_send):
                    updates_this_round += 1

        for router in routers:
            print(f"Router {router.router_id} Table: {router.routing_table}")

        print(f"Summary: {updates_this_round} routing table updates performed in Iteration {iteration}.")

        if updates_this_round == 0:
            print("\nNetwork converged! No further changes.")
            break

        time.sleep(delay_per_iteration)

def main() -> None:
    print(f"{YELLOW}Initializing Distance Vector Routing Simulation...{RESET}")
    time.sleep(1.5)

    r1 = Router(router_id=1, neighbors={2: 2, 3: 5})
    r2 = Router(router_id=2, neighbors={1: 2, 3: 1})
    r3 = Router(router_id=3, neighbors={1: 5, 2: 1})

    routers = [r1, r2, r3]

    run_distance_vector_simulation(
        routers=routers,
        max_iterations=10,
        link_failure_iter=3,
        fail_pair=(1, 2),
        delay_per_iteration=2.5
    )

if __name__ == "__main__":
    main()
