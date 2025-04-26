import math
import time
from typing import Dict, Tuple, Union, List

# Type alias for readability
RouterID = Union[int, str]

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class Router:
    def __init__(self, router_id: RouterID, neighbors: Dict[RouterID, float]):
        # Initialize a router with its ID and dictionary of neighbors and link costs
        if not isinstance(router_id, (int, str)):
            raise ValueError("router_id must be int or str.")
        for nid, cost in neighbors.items():
            if not isinstance(nid, (int, str)):
                raise ValueError("Neighbor IDs must be int or str.")
            if not (isinstance(cost, (int, float)) and cost >= 0):
                raise ValueError(f"Link cost to neighbor {nid} must be a non-negative number.")

        self.router_id = router_id
        self.neighbors = neighbors
        # Initialize routing table with self-distance 0
        self.routing_table: Dict[RouterID, Tuple[float, Union[RouterID, None]]] = {
            self.router_id: (0.0, None)
        }

    def get_distance(self, destination: RouterID) -> float:
        # Retrieve the distance to a destination, or infinity if unknown
        return self.routing_table.get(destination, (math.inf, None))[0]

    def get_filtered_routing_table(self, for_neighbor_id: RouterID) -> Dict[RouterID, Tuple[float, Union[RouterID, None]]]:
        # Apply split horizon: do not advertise routes learned from a neighbor back to it
        filtered_table = {}
        for dest, (dist, next_hop) in self.routing_table.items():
            if next_hop == for_neighbor_id:
                continue
            filtered_table[dest] = (dist, next_hop)
        return filtered_table

    def update_table_from_neighbor(self, neighbor_id: RouterID, neighbor_table: Dict[RouterID, Tuple[float, Union[RouterID, None]]]) -> bool:
        # Update routing table based on neighbor's advertised table
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

def simulate_link_failure(routers: List[Router], fail_pair: Tuple[RouterID, RouterID]) -> None:
    # Simulate a link failure by setting the cost between two routers to infinity
    a_id, b_id = fail_pair
    router_a = next((r for r in routers if r.router_id == a_id), None)
    router_b = next((r for r in routers if r.router_id == b_id), None)

    if router_a and router_b:
        if b_id in router_a.neighbors:
            router_a.neighbors[b_id] = math.inf
        if a_id in router_b.neighbors:
            router_b.neighbors[a_id] = math.inf
        print(f"{YELLOW}\n!!! WARNING: Link failure simulated between Router {a_id} and Router {b_id} (link cost set to infinity) !!!{RESET}")

def pretty_print_routing_table(router: Router) -> None:
    # Print the current routing table of a router in a readable format
    print(f"Routing table for Router {router.router_id}:")
    for dest, (dist, next_hop) in sorted(router.routing_table.items()):
        nh_display = f"via {next_hop}" if next_hop is not None else "direct"
        print(f"  Destination {dest}: cost={dist}, {nh_display}")

def run_distance_vector_simulation(
    routers: List[Router],
    max_iterations: int = 10,
    link_failure_iter: int = 3,
    fail_pair: Tuple[RouterID, RouterID] = (1, 2),
    delay_per_iteration: float = 2.5
) -> None:
    # Main simulation loop
    for iteration in range(1, max_iterations + 1):
        print(f"\n=== Iteration {iteration} ===")
        updates_this_round = 0

        # Simulate a link failure if specified
        if link_failure_iter is not None and iteration == link_failure_iter:
            simulate_link_failure(routers, fail_pair)

        all_filtered_tables = {}
        for router in routers:
            sender_id = router.router_id
            all_filtered_tables[sender_id] = {}
            for neighbor_id in router.neighbors:
                # Prepare the table to send, applying split horizon
                filtered_table = router.get_filtered_routing_table(for_neighbor_id=neighbor_id)
                all_filtered_tables[sender_id][neighbor_id] = filtered_table

        # Send routing tables and update neighbors
        for sender_router in routers:
            sender_id = sender_router.router_id
            for neighbor_id in sender_router.neighbors:
                neighbor_router = next(r for r in routers if r.router_id == neighbor_id)
                table_to_send = all_filtered_tables[sender_id][neighbor_id]
                if neighbor_router.update_table_from_neighbor(sender_id, table_to_send):
                    updates_this_round += 1

        # Print routing tables after updates
        for router in routers:
            pretty_print_routing_table(router)

        print(f"Summary: {updates_this_round} routing table updates performed in Iteration {iteration}.")

        # Check for convergence
        if updates_this_round == 0:
            print(f"{GREEN}\nNetwork converged! No further changes.{RESET}")
            break

        # Wait before next iteration to simulate real-time delay
        time.sleep(delay_per_iteration)

def main() -> None:
    # Initialize and start the simulation
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