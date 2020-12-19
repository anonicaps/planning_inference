# Description

Unified framework to solving inference tasks where the agent's model is described with a planning model and the evidence is a sequence of gapped observations denoting partial, abstract, and possibly noisy representations of the agent's states. 

# Installation
Run the following command in the root directory

~~~~
pip install -e .
~~~~

Modify the path to the Fast-Downward planner in `config.py`

~~~~
fast_downward_path = "/path/to/fast-downward/fast-downward.py"
~~~~