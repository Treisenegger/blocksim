from tqdm import tqdm
from types import MethodType
from functools import reduce
from random import randint
from tree_format import format_tree


class Player:
    def __init__(self, name, h, strat):
        self.name = name
        self.h = h
        self.strat = MethodType(strat, self)
        self.payoff = 0
        self.block_number = 0

class Block:
    def __init__(self, parent, owner, depth):
        self.parent = parent
        self.owner = owner
        self.depth = depth
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Simulation:
    def __init__(self, players, payoff, step_nr, alpha=1, beta=1):
        self.players = players
        self.step_nr = step_nr
        self.alpha = alpha
        self.beta = beta
        self.tot_h = reduce(lambda x, y: x + y, map(lambda x: x.h, players))
        self.tree = Block(None, None, 0)
        self.bc_blocks = {self.tree}
        self.bc_depth = 0
        self.calc_payoff = MethodType(payoff, self)

    def step(self):
        rand_player = randint(1, self.tot_h)

        for player in self.players:
            if rand_player <= player.h:
                owner = player
                break
            else:
                rand_player -= player.h
        
        parent_block = owner.strat(self.tree, self.bc_blocks, self.bc_depth)

        for child in parent_block.children:
            if child.owner == owner:
                print("Invalid strategy!")

        new_block = Block(parent_block, owner, parent_block.depth + 1)
        parent_block.add_child(new_block)
        owner.last_block = new_block

        if new_block.depth == self.bc_depth:
            self.bc_blocks.add(new_block)
        elif new_block.depth > self.bc_depth:
            self.bc_blocks = {new_block}
            self.bc_depth = new_block.depth
    
    def simulate(self):
        for _ in tqdm(range(self.step_nr)):
            self.step()

        while len(self.bc_blocks) > 1:
            self.bc_depth -= 1
            new_blocks = set()

            for block in self.bc_blocks:
                new_blocks.add(block.parent)

            self.bc_blocks = new_blocks

        payoff_dict = self.calc_payoff(self.bc_blocks.pop(), self.tree)

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
        print(format_tree(self.tree, lambda x: x.owner.name if not x.owner is None else 'None', lambda x: x.children))
