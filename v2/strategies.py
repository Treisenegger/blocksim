from types import MethodType


def default_strat(self, tree, bc_blocks, bc_depth, simulation):
    sel_block = None

    next_blocks = bc_blocks

    if len(bc_blocks) > 1:
        while len(next_blocks) > 1:
            old_blocks = next_blocks
            next_blocks = set()
            for block in old_blocks:
                next_blocks.add(block.parent)

        common_block = next_blocks.pop()
        block_payoff = {block: simulation.calc_payoff(block, common_block) for block in bc_blocks}
        max_payoff = max(block_payoff, key=lambda x: block_payoff[x][self]["payoff"])
        max_payoff_blocks = set(filter(lambda x: block_payoff[x][self]["payoff"] == block_payoff[max_payoff][self]["payoff"], bc_blocks))
        sel_block = max_payoff_blocks.pop()
    
    if sel_block is None:
        sel_block = bc_blocks.pop()
        bc_blocks.add(sel_block)

    return sel_block
