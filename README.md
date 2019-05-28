# BlockSim

BlockSim is a Python library for conducting simulations to test the efficiency of different mining strategies on the Bitcoin structure.

## Dependencies

To install the dependencies needed for running BlockSim, run the command

```pip install -r requirements.txt```

## Miner example

In this section we give an example of a miner implementation. This miner will implement a strategy through which it will fork only if the deepest blocks in the structure are at most two levels deeper than its last placed block. Otherwise, it will randomly mine on top of one of the deepest blocks in the structure. Also, it will publish every block instantly and will neither communicate the existence of hidden blocks nor use any blocks it is informed of.

```python
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

