from types import MethodType


def default_strat(self, payoff):
    if self.mining in self.struct.deep_blocks:
        return self.mining

    sel_block = None

    next_blocks = self.struct.deep_blocks.copy()

    if len(next_blocks) > 1:
        while len(next_blocks) > 1:
            old_blocks = next_blocks
            next_blocks = set()
            for block in old_blocks:
                next_blocks.add(block.parent)

        common_block = next_blocks.pop()
        block_payoff = {block: payoff(block, common_block, self.struct.base)
                        for block in self.struct.deep_blocks}
        for block in block_payoff:
            if self not in block_payoff[block]:
                block_payoff[block][self] = {"block_number": 0, "payoff": 0}
        max_payoff = max(block_payoff, key=lambda x: block_payoff[x][self]["payoff"])
        max_payoff_blocks = set(filter(lambda x: block_payoff[x][self]["payoff"] == block_payoff[max_payoff][self]["payoff"], self.struct.deep_blocks))
        sel_block = max_payoff_blocks.pop()
    
    if sel_block is None:
        sel_block = next_blocks.pop()

    return sel_block
