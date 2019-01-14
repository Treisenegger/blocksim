import numpy as np

from types import MethodType
from functools import reduce
from random import randint

from tqdm import tqdm

from tree_format import format_tree

from pub_strategies import default_pub_strat
from place_strategies import default_strat
from inf_strategies import default_inf_strat
from payoff import constant_payoff, alpha_beta_payoff


class Player:
    def __init__(self, name, h, strat=default_strat, publish=default_pub_strat, inform=default_inf_strat):
        self.name = name
        self.h = h
        self.strat = MethodType(strat, self)
        self.publish = MethodType(publish, self)
        self.inform = MethodType(inform, self)
        self.hidden_blocks = []
        self.known_blocks = []
        self.additional_info = dict()

    def add_hidden_block(self, block):
        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):
        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):
        self.known_blocks.append(block)


class Block:
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
    def __init__(self):
        self.base = Block(None, None, 0)
        self.base.set_visible()
        self.deep_blocks = {self.base}
        self.depth = 0
        self.last_tstamp = 0

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
    def __init__(self, players, step_nr, payoff=alpha_beta_payoff(1, 1)):
        self.players = players
        self.calc_payoff = payoff
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, map(lambda x: x.h, players))
        self.struct = Structure()
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
                publish = player.publish(self.calc_payoff)
                inform = player.inform(self.calc_payoff)
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
            if rand_player <= player.h:
                owner = player
                break
            else:
                rand_player -= player.h
        parent = owner.strat(self.calc_payoff)
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
                publish = player.publish(self.calc_payoff, True)
                inform = player.inform(self.calc_payoff, True)
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
        payoff_dict = self.calc_payoff(last_block, self.struct.base, self.struct.base)

        for player in self.players:
            player.block_number = payoff_dict[player]["block_number"] if player in payoff_dict else 0
            player.payoff = payoff_dict[player]["payoff"] if player in payoff_dict else 0

    def print_results(self):
        tot_blocks = reduce(lambda x, y: x + y, map(lambda x: x.block_number, self.players))
        tot_payoff = reduce(lambda x, y: x + y, map(lambda x: x.payoff, self.players))

        print("==========")
        for i, player in enumerate(self.players):
            print("Player: {}".format(i + 1))
            print("Hash Power: {} ({}%)".format(player.h, player.h * 100 / self.tot_h))
            print("Block Number: {} ({}%)".format(player.block_number, player.block_number * 100 / tot_blocks if tot_blocks else 0))
            print("Payoff: {} ({}%)".format(player.payoff, player.payoff * 100 / tot_payoff if tot_payoff else 0))
            print("==========")

    def print_struct(self):
        print(format_tree(self.struct.base, lambda x: x.owner.name if not x.owner is None else 'None', lambda x: x.children))
