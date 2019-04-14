"""BlockSim provides functions and classes that allow the construction of simulations
to pit different strategies for the mining of blocks for the data structure of Bitcoin
against each other.

The simulation submodule consists of the main logic behind the simulations, whilst
the payoff and players submodules consist of standard payoff functions and mining
strategies, respectively."""

from .players import *
from .payoff import constant_payoff, alpha_beta_step_payoff
from .simulation import Simulation, Block