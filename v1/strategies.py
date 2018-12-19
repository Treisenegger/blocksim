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

def one_fork_giveup_strat(self, tree, bc_blocks, bc_depth, simulation):
    if hasattr(self, "fork_depth") and bc_depth - self.fork_depth > 100:
        self.strat = MethodType(default_strat, self)
        return self.strat(tree, bc_blocks, bc_depth)

    if hasattr(self, "fork_depth") and len(bc_blocks) == 1 and list(bc_blocks)[0].owner == self:
        self.strat = MethodType(default_strat, self)
        return self.strat(tree, bc_blocks, bc_depth)

    if not hasattr(self, "last_block"):
        prev_block = next_block = tree
    else:
        prev_block = next_block = self.last_block
    for child in tree.children:
        if child.owner == self:
            next_block = child
            break

    while prev_block != next_block:
        prev_block = next_block
        for child in prev_block.children:
            if child.owner == self:
                next_block = child
                break

    if hasattr(self, "fork_depth"):
        if len(next_block.children) > 0:
            self.strat = MethodType(default_strat, self)
            return self.strat(tree, bc_blocks, bc_depth)
        else:
            return next_block
    else:
        if len(next_block.children) > 0:
            self.fork_depth = next_block.depth

        return next_block

def always_fork_strat(self, tree, bc_blocks, bc_depth, simulation):
    if not hasattr(self, "last_block"):
        prev_block = next_block = tree
    else:
        prev_block = next_block = self.last_block

    for child in prev_block.children:
        if child.owner == self:
            next_block = child
            break

    while prev_block != next_block:
        prev_block = next_block
        for child in prev_block.children:
            if child.owner == self:
                next_block = child
                break
    
    return next_block
