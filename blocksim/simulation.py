"""Classes consisting of the main logic behind the simulations."""

from functools import reduce
from random import randint

from tqdm import tqdm

# from tree_format import format_tree

from .payoff import constant_payoff, alpha_beta_step_payoff


class Block:

    """Generate block of the data structure."""

    def __init__(self, parent, owner, tstamp=-1):

        """Parameters
        ----------
        
        parent : blocksim.simulation.Block
            parent block for the new block
        owner : blocksim.miners.Miner
            miner that created the block
        tstamp : int
            timestamp of moment in which the block was published"""
        
        self.parent = parent
        self.owner = owner
        self.depth = parent.depth + 1 if parent is not None else 0
        self.tstamp = tstamp
        self.children = []
        self.is_hidden = lambda: self not in self.parent.children
        self.paid = False

    def add_child(self, child):

        """Add child block to current block.
        
        Parameters
        ----------
        
        child : blocksim.simulation.Block
            child block of current block"""

        self.children.append(child)

    def set_tstamp(self, tstamp):

        """Set timestamp of publication for current block.
        
        Parameters
        ----------
        
        tstamp : int
            timestamp of publication for current block"""

        self.tstamp = tstamp

    def set_paid(self):

        """Mark block as paid."""

        self.paid = True

    def is_paid(self):

        """Check whether block has been paid."""

        return self.paid


class Structure:

    """Generate data structure for conducting simulation."""

    def __init__(self, payoff, miners, safe_dist):

        """Parameters
        ----------
        
        payoff : function
            payoff function for simulation
        miners : list
            list of miners participating to keep track of their payoffs
        safe_dist : int
            number indicating how many blocks have to be ahead of certain block in the
            blockchain for its payoff to be given out"""

        self.base = Block(None, None, 0)
        self.base.set_paid()
        self.deep_blocks = {self.base}
        self.depth = 0
        self.last_tstamp = 0
        self.payoff = payoff
        self.safe_dist = safe_dist
        self.partial_payoff = {miner.name: {'block_number': 0, 'payoff': 0} for miner in miners}

    def add_block(self, block):

        """Add a revealed block to the data structure. Also update partial payoffs when appropriate.
        
        Parameters
        ----------
        
        block : blocksim.simulation.Block
            revealed block to add to the data structure"""

        block.set_tstamp(self.last_tstamp + 1)
        block.parent.add_child(block)

        if block.depth == self.depth:
            self.deep_blocks.add(block)
        elif block.depth > self.depth:
            self.deep_blocks = {block}
            self.depth = block.depth
            if block.depth > self.safe_dist:
                first_paid = block
                for _ in range(self.safe_dist):
                    first_paid = first_paid.parent

                last_paid = first_paid
                last_paid.set_paid()
                while last_paid.parent is not None and not last_paid.parent.is_paid():
                    last_paid = last_paid.parent
                    last_paid.set_paid()
                
                new_payoffs = self.payoff(first_paid, last_paid, self.base)

                for miner_name in new_payoffs:
                    self.partial_payoff[miner_name]['block_number'] += new_payoffs[miner_name]['block_number']
                    self.partial_payoff[miner_name]['payoff'] += new_payoffs[miner_name]['payoff']

        self.last_tstamp += 1
        

class Simulation:

    """Generate a simulation object to run simulations using certain parameters."""

    def __init__(self, miners, h, step_nr, safe_dist=0, payoff=alpha_beta_step_payoff(1, 1, 1)):

        """Parameters
        ----------
        
        miners : list
            list of miners to participate in the simulation
        h : dict
            dictionary of pairs {miner name: hash power value}. The greater
            the hash power value the likelier it is for the miner to get
            assigned the next new block
        step_nr : int
            number of blocks to generate before the simulation ends
        safe_dist : int
            number indicating how many blocks have to be ahead of a certain
            block in the blockchain for its payoff to be given out
        payoff : function
            payoff function for simulation blocks"""

        self.miners = miners
        self.h = h
        self.step_nr = step_nr
        self.tot_h = reduce(lambda x, y: x + y, h.values())
        self.struct = Structure(payoff, miners, safe_dist)
        self.hidden_blocks = []

    def add_hidden_block(self, owner, parent):

        """Generate a hidden block and inform the owner of its creation.
        
        Parameters
        ----------
        
        owner : blocksim.miners.Miner
            owner of the new block that is being created
        parent : blocksim.simulation.Block
            parent block for the new block"""

        new_block = Block(parent, owner)
        self.hidden_blocks.append(new_block)
        owner.add_hidden_block(new_block)

    def check_publishable(self, miner):

        """Spreads information based on state changes of the data structure and
        communication between miners. Firstly, the owner of the new block can choose
        to reveal any of their hidden blocks or to communicate any of them to other
        miners. After this, any miner which has gotten new information through
        the reveal of a new block or through a message received can choose to
        reveal a block or communicate blocks to other miners. This iterative
        process continues until there is a cycle in which no miners have gotten
        new information.
        
        Parameters
        ----------
        
        miner : blocksim.miners.Miner
            owner of the block generated in the current cycle"""

        updated_miners = {miner}
        while updated_miners:
            prev_miners = updated_miners
            updated_miners = set()
            publishable = set()
            informable = dict()
            for miner in prev_miners:
                publish = miner.publish(self.struct)
                inform = miner.inform(self.struct)
                if publish:
                    updated_miners = set(self.miners)
                    publishable |= publish
                if inform:
                    for i_miner in inform:
                        updated_miners.add(i_miner)
                        if i_miner not in informable:
                            informable[i_miner] = set()
                        informable[i_miner] |= inform[i_miner]
            
            for block in publishable:
                self.struct.add_block(block)
                self.hidden_blocks.remove(block)
            
            for miner_name in informable:
                for block in informable[miner_name]:
                    miner = next((x for x in self.miners if x.name == miner_name), None)
                    miner.add_known_block(block)

    def step(self):

        """Simulates one step of the experiment. Firstly, the algorithm
        chooses one miner randomly, with the probability of selecting a
        miner being determined by their hash power value divided by
        the total hash power value of all miners. After this a block
        is created with said miner as its owner. Lastly, we call the
        `blocksim.simulation.Simulation.check_publishable` method, which
        spreads information between the different miners."""

        rand_miner = randint(1, self.tot_h)
        for miner in self.miners:
            if rand_miner <= self.h[miner.name]:
                owner = miner
                break
            else:
                rand_miner -= self.h[miner.name]
        parent = owner.strat(self.struct)
        self.add_hidden_block(owner, parent)
        self.check_publishable(owner)

    def uncover_on_end(self):

        """Considering that the simulation has a finite number on steps,
        this method is called at the end of the process, to make sure that
        every miner can disclose their hidden blocks at the end of the
        simulation, for them to count towards their payoff."""

        updated_miners = set(self.miners)
        while updated_miners:
            prev_miners = updated_miners
            updated_miners = set()
            publishable = set()
            informable = dict()
            for miner in prev_miners:
                publish = miner.publish(self.struct, True)
                inform = miner.inform(self.struct, True)
                if publish:
                    updated_miners = set(self.miners)
                    publishable |= publish
                if inform:
                    for i_miner in inform:
                        updated_miners.add(i_miner)
                        if i_miner not in informable:
                            informable[i_miner] = set()
                        informable[i_miner] |= inform[i_miner]
            
            for block in publishable:
                self.struct.add_block(block)
                self.hidden_blocks.remove(block)
            
            for miner_name in informable:
                for block in informable[miner_name]:
                    miner = next((x for x in self.miners if x.name == miner_name), None)
                    miner.add_known_block(block)

    def simulate(self):

        """Conducts the simulation itself. Runs the number of steps specified
        on the instatiation of the simulation object and calculates the payoff
        that each miner receives and saves this data."""

        for _ in tqdm(range(self.step_nr)):
            self.step()

        self.uncover_on_end()

    def print_results(self):

        """Prints the results of the simulation, displaying the hash power value,
        the block number and the payoff for each of the miners."""

        tot_blocks = reduce(lambda x, y: x + y, map(lambda x: x["block_number"], self.struct.partial_payoff.values()))
        tot_payoff = reduce(lambda x, y: x + y, map(lambda x: x["payoff"], self.struct.partial_payoff.values()))

        print("==========")
        for miner in self.miners:
            print("Miner: {}".format(miner.name))
            print("Hash Power: {} ({:.2f}%)".format(self.h[miner.name], self.h[miner.name] * 100 / self.tot_h))
            print("Block Number: {} ({:.2f}%)".format(self.struct.partial_payoff[miner.name]["block_number"], self.struct.partial_payoff[miner.name]["block_number"] * 100 / tot_blocks if tot_blocks else 0))
            print("Payoff: {:.2f} ({:.2f}%)".format(self.struct.partial_payoff[miner.name]["payoff"], self.struct.partial_payoff[miner.name]["payoff"] * 100 / tot_payoff if tot_payoff else 0))
            print("==========")

    # def print_struct(self):

    #     """Displays a representation of the data structure of the conducted
    #     simulation in the terminal using the library `format_tree`."""

    #     print(format_tree(self.struct.base, lambda x: "{}-{}".format(x.owner.name, x.tstamp) if not x.owner is None else 'None', lambda x: x.children))
