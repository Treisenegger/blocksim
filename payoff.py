def calc_payoff(self, alpha):
    while len(self.bc_blocks) > 1:
        self.bc_depth -= 1
        new_blocks = set()

        for block in self.bc_blocks:
            new_blocks.add(block.parent)

        self.bc_blocks = new_blocks
    
    block = self.bc_blocks.pop()

    while block != self.tree:
        block.owner.block_number += 1
        block.owner.payoff += alpha ** block.depth
        block = block.parent