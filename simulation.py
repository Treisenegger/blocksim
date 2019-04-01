import numpy as np

from types import MethodType
from functools import reduce
from random import randint

from tqdm import tqdm

from tree_format import format_tree

from payoff import constant_payoff, alpha_beta_payoff


class Block:
    '''Object representing one block of the data structure. Each block has a parent block, an owner and a timestamp indicating when it was revealed.'''
    def __init__(self, parent, owner, tstamp=-1):
        self.parent = parent
        self.owner = owner
        self.depth = parent.depth + 1 if parent is not None else 0
        self.tstamp = tstamp
        self.children = []
        self.hidden = True

    def add_child(self, child):
        self.children.append(child)

    def set_tstamp(self, tstamp):
        self.tstamp = tstamp

    def set_visible(self):
        self.hidden = False


class Structure:
    def __init__(self, payoff):
        self.base = Block(None, None, 0)
        self.base.set_visible()
        self.deep_blocks = {self.base}
        self.depth = 0
        self.last_tstamp = 0
        self.payoff = payoff

    def add_block(self, block):
        block.set_tstamp(self.last_tstamp + 1)
        block.parent.add_child(block)

        if block.depth == self.depth:
            self.deep_blocks.add(block)
        elif block.depth > self.depth:
            self.deep_blocks = {block}
            self.depth = block.depth

        self.last_tstamp += 1
        

class Simulation:
    def __init__(self, players, h, step_nr, payoff=alpha_beta_payoff(1, 1)):
        self.players = players
        self.h = h
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, h.values())
        self.struct = Structure(payoff)
        self.hidden_blocks = []
        for player in self.players:
            player.struct = self.struct

    def add_hidden_block(self, owner, parent):
        new_block = Block(parent, owner)
        self.hidden_blocks.append(new_block)
        owner.add_hidden_block(new_block)

    def check_publishable(self, player):
        updated_players = {player}
        while updated_players:
            prev_players = updated_players
            updated_players = set()
            publishable = set()
            informable = dict()
            for player in prev_players:
                publish = player.publish(self.struct)
                inform = player.inform(self.struct)
                if publish:
                    updated_players = set(self.players)
                    publishable |= publish
                if inform:
                    for i_player in inform:
                        updated_players.add(i_player)
                        if i_player not in informable:
                            informable[i_player] = set()
                        informable[i_player] |= inform[i_player]
            
            for block in publishable:
                self.struct.add_block(block)
                block.set_visible()
                self.hidden_blocks.remove(block)
            
            for player_name in informable:
                for block in informable[player]:
                    player = next((x for x in self.players if x.name == player_name), None)
                    player.add_known_block(block)

    def step(self):
        rand_player = randint(1, self.tot_h)
        for player in self.players:
            if rand_player <= self.h[player.name]:
                owner = player
                break
            else:
                rand_player -= self.h[player.name]
        parent = owner.strat(self.struct)
        self.add_hidden_block(owner, parent)
        self.check_publishable(owner)

    def uncover_on_end(self):
        updated_players = set(self.players)
        while updated_players:
            prev_players = updated_players
            updated_players = set()
            publishable = set()
            informable = dict()
            for player in prev_players:
                publish = player.publish(self.struct, True)
                inform = player.inform(self.struct, True)
                if publish:
                    updated_players = set(self.players)
                    publishable |= publish
                if inform:
                    for i_player in inform:
                        updated_players.add(i_player)
                        if i_player not in informable:
                            informable[i_player] = set()
                        informable[i_player] |= inform[i_player]
            
            for block in publishable:
                self.struct.add_block(block)
                block.set_visible()
                self.hidden_blocks.remove(block)
            
            for player_name in informable:
                for block in informable[player]:
                    player = next((x for x in self.players if x.name == player_name), None)
                    player.add_known_block(block)

    def simulate(self):
        for _ in tqdm(range(self.step_nr)):
            self.step()

        self.uncover_on_end()

        while len(self.struct.deep_blocks) > 1:
            self.struct.depth -= 1
            new_blocks = set()

            for block in self.struct.deep_blocks:
                new_blocks.add(block.parent)

            self.struct.deep_blocks = new_blocks
        
        last_block = self.struct.deep_blocks.pop()
        self.struct.deep_blocks.add(last_block)
        payoff_dict = self.struct.payoff(last_block, self.struct.base, self.struct.base)

        for player in self.players:
            player.block_number = payoff_dict[player.name]["block_number"] if player.name in payoff_dict else 0
            player.payoff = payoff_dict[player.name]["payoff"] if player.name in payoff_dict else 0

    def print_results(self):
        tot_blocks = reduce(lambda x, y: x + y, map(lambda x: x.block_number, self.players))
        tot_payoff = reduce(lambda x, y: x + y, map(lambda x: x.payoff, self.players))

        print("==========")
        for player in self.players:
            print("Player: {}".format(player.name))
            print("Hash Power: {} ({}%)".format(self.h[player.name], self.h[player.name] * 100 / self.tot_h))
            print("Block Number: {} ({}%)".format(player.block_number, player.block_number * 100 / tot_blocks if tot_blocks else 0))
            print("Payoff: {} ({}%)".format(player.payoff, player.payoff * 100 / tot_payoff if tot_payoff else 0))
            print("==========")

    def print_struct(self):
        print(format_tree(self.struct.base, lambda x: "{}-{}".format(x.owner.name, x.tstamp) if not x.owner is None else 'None', lambda x: x.children))
