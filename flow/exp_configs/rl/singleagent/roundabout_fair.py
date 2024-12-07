"""
Benchmark for Fair Roundabout.

Roundabout with fairness criteria to ensure balanced traffic distribution,
equitable lane utilization, and efficient traffic management. The actions 
specify the desired velocity for autonomous vehicles, considering fairness.

- **Action Dimension**: (?, )
- **Observation Dimension**: (?, )
- **Horizon**: 1500 steps
"""

import sys, os
sys.path.append(os.path.abspath(os.getcwd()))
from flow.envs import RoundaboutEnv
from flow.networks import RoundaboutNetwork
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams, \
    InFlows, SumoCarFollowingParams, SumoLaneChangeParams
from flow.core.params import TrafficLightParams, VehicleParams
from flow.controllers import RLController, ContinuousRouter, SimLaneChangeController
import numpy as np

# Custom environment class for fairness
class RoundaboutFairEnv(RoundaboutEnv):
    def compute_reward(self, rl_actions, **kwargs):
        """
        Custom reward function for fairness in the roundabout.
        - Throughput reward: Encourages vehicles to reach their destinations.
        - Fairness penalty: Penalizes imbalanced lane usage and speed variance.
        """
        # Throughput: Number of vehicles successfully exited
        throughput_reward = self.k.vehicle.num_arrived()

        # Fairness: Penalize speed variance
        speeds = self.k.vehicle.get_speed(self.k.vehicle.get_ids())
        speed_variance_penalty = -np.var(speeds)

        # Fairness: Penalize lane imbalance
        lane_occupancy = [
            len(self.k.vehicle.get_ids_by_lane(edge, lane))
            for edge in self.k.network.rts_edges.values()
            for lane in range(self.k.network.num_lanes(edge))
        ]
        lane_balance_penalty = -np.std(lane_occupancy)

        # Weighted combined reward
        reward = (
            throughput_reward
            + 0.5 * speed_variance_penalty  # Weight for speed fairness / You can adjust this weight as well
            + 0.5 * lane_balance_penalty   # Weight for lane fairness
        )
        return reward

# Time horizon for a single rollout
HORIZON = 1500

# Parallelism
N_CPUS = 4    #Maximize it for faster training - I kept it at 4 for now
N_ROLLOUTS = N_CPUS * 4
SCALING = 1

# Autonomous vehicle penetration rate
AV_FRAC = 0.2  # Higher fraction of autonomous vehicles

# Vehicle configurations
vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="all_checks",
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=0,
    ),
    num_vehicles=10 * SCALING
)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode=9,
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=0,
    ),
    num_vehicles=5 * SCALING
)

# Setting AV penetration rates for 10% and 25% testing
penetration_rates = [0.1, 0.25]

for rate in penetration_rates:
    AV_FRAC = rate
    print(f"Running experiment with {AV_FRAC * 100}% AV penetration...")

    # Define inflows to ensure fairness with the current AV_FRAC value
    flow_rate = 2000 * SCALING
    inflow = InFlows()
    inflow.add(
        veh_type="human",
        edge="inflow_highway",
        vehs_per_hour=flow_rate * (1 - AV_FRAC),
        departLane="random",
        departSpeed=10
    )
    inflow.add(
        veh_type="rl",
        edge="inflow_highway",
        vehs_per_hour=flow_rate * AV_FRAC,
        departLane="random",
        departSpeed=10
    )

# Fairness environment parameters
additional_env_params = {
    "target_velocity": 30,
    "num_observed": 10,
    "max_accel": 3.0,
    "max_decel": 3.0,
    "fairness_criteria": "lane_equity", 
    "reset_inflow": False,
}

# Network parameters
additional_net_params = {
    "radius_ring": 50,
    "lanes": 3,
    "speed_limit": 25,
}

# Traffic light configurations
traffic_lights = TrafficLightParams()

# Define flow parameters
flow_params = dict(
    exp_tag="fair_roundabout",

    env_name=RoundaboutFairEnv,  

    network=RoundaboutNetwork,

    simulator='traci',

    sim=SumoParams(
        sim_step=0.5,
        render=True,  # Visualization enabled for fairness simulation
        print_warnings=False,
        restart_instance=True,
    ),

    env=EnvParams(
        warmup_steps=40,
        sims_per_step=1,
        horizon=HORIZON,
        additional_params=additional_env_params,
    ),

    net=NetParams(
        inflows=inflow,
        additional_params=additional_net_params,
    ),

    veh=vehicles,

    initial=InitialConfig(
        spacing="uniform",
        min_gap=5,
        lanes_distribution=float("inf"),
    ),

    tls=traffic_lights,
)

# Debugging: print flow parameters
if __name__ == "__main__":
    print("Flow parameters for fairness experiment:")
    for key, value in flow_params.items():
        print(f"{key}: {value}")
