"""Classes consisting of the main logic behind the simulations."""

import numpy as np

from types import MethodType
from functools import reduce
from random import randint

from tqdm import tqdm

from tree_format import format_tree

from .payoff import constant_payoff, alpha_beta_step_payoff


class Block:

    """Generate block of the data structure."""

    def __init__(self, parent, owner, tstamp=-1):

        """Parameters
        ----------
        
        parent : Block
            parent block for the new block
        owner : Player
            player that created the block
        tstamp : int
            timestamp of moment in which the block was revealed"""
        
        self.parent = parent
        self.owner = owner
        self.depth = parent.depth + 1 if parent is not None else 0
        self.tstamp = tstamp
        self.children = []
        self.hidden = True

    def add_child(self, child):

        """Add child block to current block.
        
        Parameters
        ----------
        
        child : Block
            child block of current block"""

        self.children.append(child)

    def set_tstamp(self, tstamp):

        """Set timestamp of revelation for current block.
        
        Parameters
        ----------
        
        tstamp : int
            timestamp in of revelation for current block"""

        self.tstamp = tstamp

    def set_visible(self):

        """Reveal current block."""

        self.hidden = False


class Structure:

    """Generate data structure for conducting simulation."""

    def __init__(self, payoff):

        """Parameters
        ----------
        
        payoff : function
            payoff function for simulation"""

        self.base = Block(None, None, 0)
        self.base.set_visible()
        self.deep_blocks = {self.base}
        self.depth = 0
        self.last_tstamp = 0
        self.payoff = payoff

    def add_block(self, block):

        """Add a revealed block to the data structure.
        
        Parameters
        ----------
        
        block : Block
            revealed block to add to the data structure"""

        block.set_tstamp(self.last_tstamp + 1)
        block.parent.add_child(block)

        if block.depth == self.depth:
            self.deep_blocks.add(block)
        elif block.depth > self.depth:
            self.deep_blocks = {block}
            self.depth = block.depth

        self.last_tstamp += 1
        

class Simulation:

    """Generate a simulation object to run simulations using certain parameters."""

    def __init__(self, players, h, step_nr, payoff=alpha_beta_step_payoff(1, 1, 1)):

        """Parameters
        ----------
        
        players : list
            list of players to participate in the simulation
        h : dict
            dictionary of pairs {player name: hash power value}. The greater the
            hash power value the likelier it is for the player to get assigned
            the next new block
        step_nr : int
            number of blocks to generate before the simulation ends
        payoff : function
            payoff function for simulation blocks"""

        self.players = players
        self.h = h
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, h.values())
        self.struct = Structure(payoff)
        self.hidden_blocks = []
        self.results = dict()

    def add_hidden_block(self, owner, parent):

        """Generate a hidden block and inform the owner of its creation.
        
        Parameters
        ----------
        
        owner : Player
            owner of the new block that is being created
        parent : Block
            parent block for the new block"""

        new_block = Block(parent, owner)
        self.hidden_blocks.append(new_block)
        owner.add_hidden_block(new_block)

    def check_publishable(self, player):

        """Spreads information based on state changes of the data structure and
        communication between players. Firstly, the owner of the new block can choose
        to reveal any of their hidden blocks or to communicate any of them to other
        players. After this, any player which has gotten new information through
        the reveal of a new block or through a message received can choose to
        reveal a block or communicate blocks to other players. This iterative
        process continues until there is a cycle in which no players have gotten
        new information.
        
        Parameters
        ----------
        
        player : Player
            owner of the block generated in the current cycle"""

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

        """Simulates one step of the experiment. Firstly, the algorithm
        chooses one player randomly, with the probability of selecting a
        player being determined by their hash power value divided by
        the total hash power value of all players. After this a block
        is created with said player as its owner. Lastly, we call the
        ``check_publishable`` method, which spreads information between
        the different players."""

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

        """Considering that the simulation has a finite number on steps,
        this method is called at the end of the process, to make sure that
        every player can disclose their hidden blocks at the end of the
        simulation, for them to count towards their payoff."""

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

        """Conducts the simulation itself. Runs the number of steps specified
        on the instatiation of the simulation object and calculates the payoff
        that each player receives and saves this data."""

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
            self.results[player.name] = dict()
            self.results[player.name]["block_number"] = payoff_dict[player.name]["block_number"] if player.name in payoff_dict else 0
            self.results[player.name]["payoff"] = payoff_dict[player.name]["payoff"] if player.name in payoff_dict else 0

    def print_results(self):

        """Prints the results of the simulation, displaying the hash power value,
        the block number and the payoff for each of the players."""

        tot_blocks = reduce(lambda x, y: x + y, map(lambda x: x["block_number"], self.results.values()))
        tot_payoff = reduce(lambda x, y: x + y, map(lambda x: x["payoff"], self.results.values()))

        print("==========")
        for player in self.players:
            print("Player: {}".format(player.name))
            print("Hash Power: {} ({}%)".format(self.h[player.name], self.h[player.name] * 100 / self.tot_h))
            print("Block Number: {} ({}%)".format(self.results[player.name]["block_number"], self.results[player.name]["block_number"] * 100 / tot_blocks if tot_blocks else 0))
            print("Payoff: {} ({}%)".format(self.results[player.name]["payoff"], self.results[player.name]["payoff"] * 100 / tot_payoff if tot_payoff else 0))
            print("==========")

    def print_struct(self):

        """Displays a representation of the data structure of the conducted
        simulation in the terminal using the library ``format_tree``."""

        print(format_tree(self.struct.base, lambda x: "{}-{}".format(x.owner.name, x.tstamp) if not x.owner is None else 'None', lambda x: x.children))
