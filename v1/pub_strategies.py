def default_pub_strat(self, payoff, end=False):
    prev_blocks = self.hidden_blocks
    self.hidden_blocks = []
    return set(prev_blocks)

def selfish_pub_strat(self, payoff, end=False):
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
