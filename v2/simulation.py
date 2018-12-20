from tqdm import tqdm
from types import MethodType
from functools import reduce
from tree_format import format_tree
import numpy as np


class Player:
    def __init__(self, name, h, strat, is_hidden=lambda x, y: False):
        self.name = name
        self.h = h
        self.strat = MethodType(strat, self)
        self.is_hidden = is_hidden
        self.mining = None


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
        self.calc_payoff = payoff
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, map(lambda x: x.h, players))
        self.struct = Structure()
        self.real_last_tstamp = 0
        self.next_blocks = {player: self.struct.base for player in self.players}
        self.next_times = {self.players[i]: t/self.players[i].h
                           for i, t in enumerate(np.random.geometric(p=1/self.tot_h, size=len(self.players)))}
        for player in self.players:
            player.struct = self.struct
            player.mining = self.struct.base

    def add_hidden_block(self, owner, parent):
        pass

    def step(self):
        min_time = min(self.next_times.values())
        self.real_last_tstamp += min_time
        visible_change = False
        for player in self.players:
            if self.next_times[player] == min_time:
                if not player.is_hidden(self.next_blocks[player], self.real_last_tstamp):
                    self.struct.last_tstamp = self.real_last_tstamp
                    self.struct.add_block(player, self.next_blocks[player])

                    visible_change = True

                else:
                    self.add_hidden_block(player, self.next_blocks[player])
                
                self.next_blocks[player] = None
                self.next_times[player] -= min_time

        self.new_targets(visible_change)
    
    def new_targets(self, visible_change):
        new_times = np.random.geometric(p=1/self.tot_h, size=len(self.players))
        for i, player in enumerate(self.players):
            if visible_change or self.next_blocks[player] is None:
                next_block = player.strat(self.calc_payoff)
                if next_block != self.next_blocks[player]:
                    self.next_blocks[player] = next_block
                    self.next_times[player] = new_times[i]/player.h
                    player.mining = next_block


    def uncover_hidden(self, block=None, all=False):
        pass

    def simulate(self):
        for _ in tqdm(range(self.step_nr)):
            self.step()

        while len(self.struct.deep_blocks) > 1:
            self.struct.depth -= 1
            new_blocks = set()

            for block in self.struct.deep_blocks:
                new_blocks.add(block.parent)

            self.struct.deep_blocks
        
        last_block = self.struct.deep_blocks.pop()
        self.struct.deep_blocks.add(last_block)
        payoff_dict = self.calc_payoff(last_block, self.struct.base, self.struct.base)

        for player in self.players:
            player.block_number = payoff_dict[player]["block_number"]
            player.payoff = payoff_dict[player]["payoff"]

    def print_results(self):
        tot_blocks = reduce(lambda x, y: x + y, map(lambda x: x.block_number, self.players))
        tot_payoff = reduce(lambda x, y: x + y, map(lambda x: x.payoff, self.players))

        print("==========")
        for i, player in enumerate(self.players):
            print("Player: {}".format(i + 1))
            print("Hash Power: {} ({}%)".format(player.h, player.h * 100 / self.tot_h))
            print("Block Number: {} ({}%)".format(player.block_number, player.block_number * 100 / tot_blocks))
            print("Payoff: {} ({}%)".format(player.payoff, player.payoff * 100 / tot_payoff))
            print("==========")

    def print_struct(self):
        print(format_tree(self.struct.base, lambda x: x.owner.name if not x.owner is None else 'None', lambda x: x.children))
