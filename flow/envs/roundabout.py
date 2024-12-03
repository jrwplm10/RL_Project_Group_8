import numpy as np
from gym.spaces.box import Box

class RoundaboutEnv:
    """
    RoundaboutEnv.

    Simulates traffic dynamics in a roundabout system. This environment
    trains vehicles to navigate the roundabout efficiently while minimizing
    delays and avoiding collisions.

    States:
        The state space includes vehicle positions, velocities, and lane
        occupancies in the roundabout and its approaches.

    Actions:
        Actions specify the desired speed or acceleration of RL-controlled
        vehicles in specific segments.

    Rewards:
        Rewards are based on traffic throughput and penalizing unnecessary
        delays or collisions.
    """

    def __init__(self, env_params, sim_params, network, simulator='traci'):
        """Initialize RoundaboutEnv."""
        super().__init__(env_params, sim_params, network, simulator)

        for p in ['controlled_segments', 'observed_segments', 'max_accel', 'max_decel']:
            if p not in env_params.additional_params:
                raise KeyError(f'Environment parameter "{p}" not supplied.')

        # Segment definitions and control settings
        self.env_params = env_params
        self.sim_params = sim_params
        self.network = network

        self.controlled_segments = env_params.additional_params.get(
            "controlled_segments", [])
        self.observed_segments = env_params.additional_params.get(
            "observed_segments", [])
        self.symmetric = env_params.additional_params.get("symmetric", True)

        self.action_index = self._initialize_action_index()

    def _initialize_action_index(self):
        """
        Initialize the mapping for actions to specific segments.
        """
        action_index = {}
        offset = 0
        for edge, num_segments, controlled in self.controlled_segments:
            if controlled:
                num_lanes = self.network.num_lanes(edge)
                segment_count = num_segments * (num_lanes if not self.symmetric else 1)
                action_index[edge] = (offset, offset + segment_count)
                offset += segment_count
        return action_index

    @property
    def observation_space(self):
        """Define the observation space."""
        num_obs = sum(
            segment[1] * self.network.num_lanes(segment[0])
            for segment in self.observed_segments
        ) * 2  # velocity + density
        return Box(low=0.0, high=np.inf, shape=(num_obs,), dtype=np.float32)

    @property
    def action_space(self):
        """Define the action space."""
        action_size = sum(
            segment[1] * (self.network.num_lanes(segment[0]) if not self.symmetric else 1)
            for segment in self.controlled_segments if segment[2]
        )
        max_accel = self.env_params.additional_params.get("max_accel", 1)
        max_decel = self.env_params.additional_params.get("max_decel", 1)
        return Box(
            low=-max_decel, high=max_accel, shape=(action_size,), dtype=np.float32)

    def get_state(self):
        """Get the current state of the environment."""
        states = []
        for edge, num_segments in self.observed_segments:
            edge_length = self.network.edge_length(edge)
            slice_positions = np.linspace(0, edge_length, num_segments + 1)
            for i in range(num_segments):
                vehicles = self.network.get_vehicles_in_segment(edge, slice_positions[i], slice_positions[i + 1])
                density = len(vehicles) / self.network.segment_length(edge, num_segments)
                avg_speed = np.mean([self.network.get_speed(veh) for veh in vehicles]) if vehicles else 0
                states.extend([density, avg_speed])
        return np.array(states)

    def _apply_rl_actions(self, rl_actions):
        """Apply the RL actions."""
        for edge, (start_idx, end_idx) in self.action_index.items():
            edge_actions = rl_actions[start_idx:end_idx]
            num_segments = len(edge_actions)
            segment_positions = np.linspace(0, self.network.edge_length(edge), num_segments + 1)
            for i, action in enumerate(edge_actions):
                vehicles = self.network.get_vehicles_in_segment(edge, segment_positions[i], segment_positions[i + 1])
                for veh in vehicles:
                    self.network.set_vehicle_speed(veh, action)

    def compute_reward(self, rl_actions, **kwargs):
        """Compute the reward."""
        throughput = self.network.get_outflow_rate() / 1000.0
        delays = sum(self.network.get_vehicle_delay(veh) for veh in self.network.get_ids())
        return throughput - 0.1 * delays

    def reset(self):
        """Reset the environment."""
        self.network.reset()
        return self.get_state()
