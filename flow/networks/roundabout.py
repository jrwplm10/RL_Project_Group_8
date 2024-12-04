from flow.core.params import InitialConfig
from flow.core.params import TrafficLightParams
from flow.networks.base import Network
import numpy as np

ADDITIONAL_NET_PARAMS = {
    # the factor multiplying number of lanes.
    "scaling": 1,
    # edge speed limit
    'speed_limit': 23
}

class RoundaboutNetwork(Network):
    """Network class for roundabout simulations.

    This network represents a configurable roundabout with a central circular
    section and connecting approaches.

    Requires from net_params:

    * **scaling** : the factor for the size of the roundabout
    * **speed_limit** : the speed limit on the roundabout and approaches

    Usage
    -----
    >>> from flow.core.params import NetParams
    >>> from flow.core.params import VehicleParams
    >>> from flow.core.params import InitialConfig
    >>> from flow.networks import RoundaboutNetwork
    >>>
    >>> network = RoundaboutNetwork(
    >>>     name='roundabout',
    >>>     vehicles=VehicleParams(),
    >>>     net_params=NetParams(
    >>>         additional_params={
    >>>             'scaling': 1,
    >>>             'speed_limit': 15,
    >>>         },
    >>>     )
    >>> )
    """

    def __init__(self,
                 name,
                 vehicles,
                 net_params,
                 initial_config=InitialConfig(),
                 traffic_lights=TrafficLightParams()):
        """Instantiate the network class."""
        for p in ADDITIONAL_NET_PARAMS.keys():
            if p not in net_params.additional_params:
                raise KeyError('Network parameter "{}" not supplied'.format(p))

        super().__init__(name, vehicles, net_params, initial_config,
                         traffic_lights)

    def specify_nodes(self, net_params):
        """Define the nodes of the roundabout network."""
        scaling = net_params.additional_params.get("scaling", 1)
        radius = 20 * scaling

        nodes = [
            {"id": "center", "x": 0, "y": 0, "type": "priority", "radius": radius},
            {"id": "entry_1", "x": -radius, "y": 2 * radius},
            {"id": "entry_2", "x": 2 * radius, "y": radius},
            {"id": "entry_3", "x": radius, "y": -2 * radius},
            {"id": "entry_4", "x": -2 * radius, "y": -radius}
        ]
        return nodes

    def specify_edges(self, net_params):
        """Define the edges connecting nodes."""
        scaling = net_params.additional_params.get("scaling", 1)
        speed = net_params.additional_params['speed_limit']

        edges = [
            {"id": "ring", "from": "center", "to": "center",
             "length": 2 * 3.14 * 20 * scaling, "numLanes": scaling, "speed": speed},
            {"id": "in_1", "from": "entry_1", "to": "center",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "in_2", "from": "entry_2", "to": "center",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "in_3", "from": "entry_3", "to": "center",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "in_4", "from": "entry_4", "to": "center",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "out_1", "from": "center", "to": "entry_1",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "out_2", "from": "center", "to": "entry_2",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "out_3", "from": "center", "to": "entry_3",
             "length": 30 * scaling, "numLanes": 1, "speed": speed},
            {"id": "out_4", "from": "center", "to": "entry_4",
             "length": 30 * scaling, "numLanes": 1, "speed": speed}
        ]
        return edges

    def specify_routes(self, net_params):
        """Define the routes through the network."""
        rts = {
            "in_1": ["in_1", "ring", "out_3"],
            "in_2": ["in_2", "ring", "out_4"],
            "in_3": ["in_3", "ring", "out_1"],
            "in_4": ["in_4", "ring", "out_2"]
        }
        return rts

    def specify_edge_starts(self):
        """Define the starting points of edges."""
        return [("ring", 0), ("in_1", 0), ("out_1", 30),
                ("in_2", 60), ("out_2", 90),
                ("in_3", 120), ("out_3", 150),
                ("in_4", 180), ("out_4", 210)]
