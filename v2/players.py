from random import sample


class DefPlayerRandom:
    def __init__(self, name):
        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.struct = None

    def add_hidden_block(self, block):
        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):
        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):
        self.known_blocks.append(block)

    def strat(self, payoff):
        return sample(self.struct.deep_blocks, 1)[0]

    def publish(self, payoff, end=False):
        prev_blocks = self.hidden_blocks
        self.hidden_blocks = []
        return set(prev_blocks)

    def inform(self, payoff, end=False):
        return dict()


class DefPlayer:
    def __init__(self, name):
        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.struct = None

    def add_hidden_block(self, block):
        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):
        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):
        self.known_blocks.append(block)

    def strat(self, payoff):
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
                if self.name not in block_payoff[block]:
                    block_payoff[block][self.name] = {"block_number": 0, "payoff": 0}
            max_payoff = max(block_payoff, key=lambda x: block_payoff[x][self.name]["payoff"])
            max_payoff_blocks = set(filter(lambda x: block_payoff[x][self.name]["payoff"] == block_payoff[max_payoff][self.name]["payoff"], self.struct.deep_blocks))
            sel_block = max_payoff_blocks.pop()
        else:
            sel_block = next_blocks.pop()

        return sel_block

    def publish(self, payoff, end=False):
        prev_blocks = self.hidden_blocks
        self.hidden_blocks = []
        return set(prev_blocks)

    def inform(self, payoff, end=False):
        return dict()


class SelfPlayer:
    def __init__(self, name):
        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.just_forked = False
        self.first_block = None
        self.last_published = None
        self.struct = None

    def add_hidden_block(self, block):
        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):
        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):
        self.known_blocks.append(block)

    def strat(self, payoff):
        if self.hidden_blocks:
            return self.hidden_blocks[-1]
        
        next_blocks = self.struct.deep_blocks.copy()

        if self.last_published is not None and self.last_published.depth == self.struct.depth:
            if len(self.struct.deep_blocks) == 1:
                self.just_forked = True
            sel_block = self.last_published
        else:
            sel_block = next_blocks.pop()
            self.just_forked = True

        return sel_block

    def publish(self, payoff, end=False):
        if end:
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = list(filter(lambda x: x.parent.hidden, self.hidden_blocks))
            return set(filter(lambda x: not x.parent.hidden, prev_blocks))

        if self.just_forked:
            self.just_forked = False
            self.first_block = self.hidden_blocks[-1]
            return set()
        elif self.hidden_blocks:
            if self.hidden_blocks == [self.first_block]:
                if self.first_block.depth == self.struct.depth:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = []
                    self.last_published = self.first_block
                    return set(prev_blocks)
                else:
                    return set()
            else:
                if self.hidden_blocks[-1].depth <= self.struct.depth + 1:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.hidden, self.hidden_blocks))
                    publish = set(filter(lambda x: not x.parent.hidden, prev_blocks))
                    self.last_published = max(publish, key=lambda x: x.depth)
                    return publish
                else:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.hidden or x.depth > self.struct.depth, self.hidden_blocks))
                    publish = set(filter(lambda x: not x.parent.hidden and x.depth <= self.struct.depth, prev_blocks))
                    self.last_published = max(publish, default=self.last_published, key=lambda x: x.depth)
                    return publish
        else:
            return set()

    def inform(self, payoff, end=False):
        return dict()

class AFPlayer:
    def __init__(self, name):
        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.last_block = None
        self.struct = None

    def add_hidden_block(self, block):
        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):
        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):
        self.known_blocks.append(block)

    def strat(self, payoff):
        if self.last_block:
            return self.last_block
        else:
            block = self.struct.deep_blocks.pop()
            self.struct.deep_blocks.add(block)
            return block

    def publish(self, payoff, end=False):
        if self.hidden_blocks:
            self.last_block = self.hidden_blocks[-1]
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = []
            return set(prev_blocks)
        else:
            return set()

    def inform(self, payoff, end=False):
        return dict()
