## PPO-RND-Pommerman

This repository contains the material used for the Pommerman project.
The methods used to get a winrate of over 50 percent over 3 simpleagents was PPO together with random network distillation.

Several files can be found including:
- [Notebook with results and pre-trained model to run tests](MainResults.ipynb)
- [Notebook with code used for training](MainTraining.ipynb)
- [Python file that changes the pommerman enviornment to an input used by our model](convertInputMapToTrainingLayers.py)

### Methods

**Required:**

- [Exploration by Random Network Distillation](https://arxiv.org/abs/1810.12894)
- [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)
