To run one of the experimental scenarios:

1) Find a scenario under exp_configs. For example: exp_configs/rl/singleagent/bottleneck0_benchmark.py

2) Run using the train.py file, as follows:
python train.py bottleneck0_benchmark

(NOTE: use just the filename only. Train.py is set up to figure the rest of the path from the filename you put)


# some TODOS:

-Better sumo setup for SUMO_HOME (it keeps going to this webpage to fetch files: https://sumo.dlr.de/xsd/)
-How to visualize a trained policy? Or see loss/reward over time???
-What is RLlib? I think understanding this might help a lot with the flow.