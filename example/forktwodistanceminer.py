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