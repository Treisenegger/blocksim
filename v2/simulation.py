from types import MethodType
from functools import reduce
import numpy as np


class Player:
    def __init__(self, name, h, strat):
        self.name = name
        self.h = h
        self.strat = MethodType(strat, self)


class Block:
    def __init__(self, parent, owner, depth, t_stamp):
        self.parent = parent
        self.owner = owner
        self.depth = depth
        self.t_stamp = t_stamp
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class Structure:
    def __init__(self):
        self.base = Block(None, None, 0, 0)
        self.deep_blocks = {self.base}
        self.depth = 0
        self.last_tstamp = 0

    def add_block(self, owner, parent):
        new_block = Block(parent, owner, parent.depth + 1, self.last_tstamp)
        parent.add_child(new_block)
        owner.last_block = new_block

        if new_block.depth == self.depth:
            self.deep_blocks.add(new_block)
        elif new_block.depth > self.depth:
            self.deep_blocks = {new_block}
            self.depth = new_block.depth
        

class Simulation:
    def __init__(self, players, payoff, step_nr):
        self.players = players
        self.calc_payoff = MethodType(payoff, self)
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, map(lambda x: x.h, players))
        self.struct = Structure()
        self.real_last_tstamp = 0
        self.next_blocks = {player: self.tree for player in self.players}
        self.next_times = {self.players[i]: t/self.players[i].h
                           for i, t in enumerate(np.random.geometric(p=1/self.tot_h, size=len(self.players)))}
        for player in self.players:
            player.struct = self.struct

    def step(self):
        min_time = min(self.next_times.values())
        self.real_last_tstamp += min_time
        visible_change = False
        for player in self.players:
            if self.next_times[player] == min_time:
                if not player.is_hidden(self.next_blocks[player], min_time):
                    self.struct.last_tstamp = self.real_last_tstamp
                    self.struct.add_block(player, self.next_blocks[player])

                    visible_change = True
                
                self.next_blocks[player] = None
                self.next_times[player] -= min_time
        
        new_times = np.random.geometric(p=1/self.tot_h, size=len(self.players))
        for i, player in enumerate(self.players):
            if visible_change or self.next_blocks[player] is None:
                next_block = player.strat(self.calc_payoff)
                if next_block != self.next_blocks[player]:
                    self.next_blocks[player] = next_block
                    self.next_times[player] = new_times[i]/player.h
    
    def uncover_hidden(self, block=None, all=False):
        pass

    def simulate(self)
        pass
