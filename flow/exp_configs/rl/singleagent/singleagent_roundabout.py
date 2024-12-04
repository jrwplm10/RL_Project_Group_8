from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams, \
    InFlows, SumoCarFollowingParams, SumoLaneChangeParams
from flow.core.params import VehicleParams
from flow.controllers import RLController, ContinuousRouter, SimLaneChangeController
from flow.envs import RoundaboutEnv
from flow.networks import RoundaboutNetwork

# time horizon of a single rollout
HORIZON = 2000  # Increased to run longer simulations
# number of parallel workers
N_CPUS = 4  # Increased for more parallelism
# number of rollouts per training iteration
N_ROLLOUTS = N_CPUS * 4

SCALING = 1
NUM_LANES = 4  # Increased number of lanes in the roundabout
AV_FRAC = 0.15  # Higher fraction of autonomous vehicles

# Vehicle parameters
vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    lane_change_controller=(SimLaneChangeController, {}),
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode="all_checks",
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=0,
    ),
    num_vehicles=15 * SCALING  # Increased number of human vehicles
)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    lane_change_controller=(SimLaneChangeController, {}),
    routing_controller=(ContinuousRouter, {}),
    car_following_params=SumoCarFollowingParams(
        speed_mode=9,
    ),
    lane_change_params=SumoLaneChangeParams(
        lane_change_mode=0,
    ),
    num_vehicles=5 * SCALING  # Increased number of RL vehicles
)

# Inflows for roundabout
flow_rate = 3000 * SCALING  # Higher traffic density
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

# Environment-specific parameters
additional_env_params = {
    "target_velocity": 35,  # Higher target speed
    "num_observed": 8,      # Observe more vehicles
    "max_accel": 3.0,       # Higher acceleration limit
    "max_decel": 3.0,       # Higher deceleration limit
    "ring_length": None,
}

# Network-specific parameters
additional_net_params = {
    "radius_ring": 40,  # Larger roundabout radius
    "lanes": NUM_LANES,
    "speed_limit": 25,  # Increased speed limit
}

# Define the flow parameters
flow_params = dict(
    exp_tag="RoundaboutCase",

    env_name=RoundaboutEnv,

    network=RoundaboutNetwork,

    simulator='traci',

    sim=SumoParams(
        sim_step=0.5,
        render=True,  # Enable rendering to visualize the simulation
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
)

# Debugging: print the flow parameters to verify correctness
print("Flow parameters:")
for key, value in flow_params.items():
    print(f"{key}: {value}")
