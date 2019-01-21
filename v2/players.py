class DefPlayer:
    def __init__(self, name):
        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.additional_info = dict()
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
        self.additional_info = dict()
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
        
        self.additional_info['just_forked'] = True

        return sel_block

    def publish(self, payoff, end=False):
        if end:
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = list(filter(lambda x: x.parent.hidden, self.hidden_blocks))
            return set(filter(lambda x: not x.parent.hidden, prev_blocks))

        if 'just_forked' in self.additional_info and self.additional_info['just_forked']:
            self.additional_info['just_forked'] = False
            self.additional_info['first_block'] = self.hidden_blocks[-1]
            return set()
        elif 'first_block' in self.additional_info and self.hidden_blocks:
            if self.hidden_blocks == [self.additional_info['first_block']]:
                if self.hidden_blocks[-1].depth == self.struct.depth:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = []
                    return set(prev_blocks)
                else:
                    return set()
            else:
                if self.hidden_blocks[-1].depth <= self.struct.depth + 1:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.hidden, self.hidden_blocks))
                    return set(filter(lambda x: not x.parent.hidden, prev_blocks))
                else:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.hidden or x.depth > self.struct.depth, self.hidden_blocks))
                    return set(filter(lambda x: not x.parent.hidden and x.depth <= self.struct.depth, prev_blocks))
        else:
            return set()

    def inform(self, payoff, end=False):
        return dict()
