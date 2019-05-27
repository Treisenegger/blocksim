"""BlockSim provides functions and classes that allow the construction of simulations
to pit different strategies for the mining of blocks for the data structure of Bitcoin
against each other.

The simulation submodule consists of the main logic behind the simulations, whilst
the payoff and miners submodules consist of standard payoff functions and mining
strategies, respectively.

The file `experiment.py`, located outside of this package, provides a standard
example on how to run simulations. In order to do this you need to import the
`blocksim.simulation.Simulation` class, the miners you want to use and the
payoff function to be utilized. After this you need to instantiate the
`blocksim.simulation.Simulation` class, providing it with a list containing
the instantiated miners which will participate, a dictionary containing the
pairs `miner_name: hash_power`, the amount of blocks that need to be placed
after a certain block in the blockchain for it to be paid off and the payoff
function for calculating individual earnings.

Afterwards, you will need to call the `blocksim.simulation.Simulation.simulate`
method on the `blocksim.simulation.Simulation` instantiation, as well as the
`blocksim.simulation.Simulation.print_results` method for displaying the
results obtained through the experiment. In order to understand how to create
custom miners read the documentation section pertaining to the
`blocksim.miners` sub-module."""

from .miners import *
from .payoff import constant_payoff, alpha_beta_step_payoff
from .simulation import Simulation, Block