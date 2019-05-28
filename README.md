# BlockSim

BlockSim is a Python 3.6 library for conducting simulations to test the efficiency of different mining strategies on the Bitcoin structure.

## Dependencies

To install the dependencies needed for running BlockSim, run the command

```pip install -r requirements.txt```

## Miner example

In this section we give an example of a miner implementation. This miner will implement a strategy through which it will fork only if the deepest blocks in the structure are at most two levels deeper than its last placed block. Otherwise, it will randomly mine on top of one of the deepest blocks in the structure. Also, it will publish every block instantly and will neither communicate the existence of hidden blocks nor use any blocks it is informed of.

```python
import sys
from random import sample

sys.path.append("./")

from blocksim import Miner

class ForkTwoDistanceMiner(Miner):
    def __init__(self, name):
        super().__init__(name)
        self.last_block = None

    def strat(self, struct):
        if self.last_block is None or self.last_block.depth < struct.depth - 2:
            return sample(struct.deep_blocks, 1)[0]
        else:
            return self.last_block

    def publish(self, struct, end=False):
        if self.hidden_blocks:
            self.last_block = self.hidden_blocks[-1]
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = []
            return set(prev_blocks)
        else:
            return set()
```

## Running the simulation

To run the simulation we need to import the miners we are going to use, the ```Simulation``` object and the payoff function we plan on setting. Afterwards, we have to create a list containing all instatiations of the different miners with their respective names and a dictionary containing the pairs ```miner_name: hash_power```. Lastly, we need to instantiate the ```Simulation``` object using the miner list, the hash power dictionary, the step number, the safe distance and the payoff function as inputs. After this, we just need to execute the ```simulate``` and ```print_results``` methods on the ```Simulation``` object to run the simulation. An example of this process is displayed below, using the same miner implemented above, which is also implemented in the miners file which can be imported as part of the package.

```python
import sys

sys.path.append("./")

from blocksim import Miner, Simulation, alpha_beta_step_payoff
from forktwodistanceminer import ForkTwoDistanceMiner

if __name__ == "__main__":
    players = []

    players.append(ForkTwoDistanceMiner('Fork Two Distance Miner'))
    players.append(Miner('Default Random Miner'))

    h = {'Fork Two Distance Miner': 1,
        'Default Random Miner': 1}

    sim = Simulation(players, h, 10000, safe_dist=0, payoff=alpha_beta_step_payoff(1, 1, 1))
    sim.simulate()
    sim.print_results()
```

Both of the previous examples are available in the example folder for testing.
