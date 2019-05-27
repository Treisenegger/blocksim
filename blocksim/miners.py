"""Standard miner strategies for conducting the experiments. Each miner is generated
with a name that serves as its identificator. Also, each miner has to have 6 methods
called `add_hidden_block`, which saves a new hidden block created by the miner,
`delete_hidden_block`, which deletes the reference to a hidden block created by the
miner after revealing it, `add_known_block`, which saves a hidden block created by
another miner, `strat`, which chooses a block to mine on top of, `publish`,
which chooses blocks to reveal, and `inform`, which chooses blocks to communicate
to other miners.

To create a new miner you need to create a class that inherits from the `Miner`
class and overrides the methods you want to modify. Miner is a class model
describing the different elements a miner has to possess to function with the
implemented simulation. It implements the default strategy choosing randomly
from the deepest blocks when there is a tie."""

from random import sample

from .simulation import Block

class Miner:

    """Generate miner that uses the default strategy but when there is a tie in
    max depth the algorithm chooses randomly between the deepest blocks to mine."""

    def __init__(self, name):

        """Parameters
        ---------
        
        name : string
            identifier for the miner. When creating a new instance of a
            miner the method has to receive a name which will serve as
            its identifier. This parameter has to be saved as an attribute
            called name."""

        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []

    def add_hidden_block(self, block):

        """This method is called when the miner finds a new block for the
        structure. Every block is created as hidden by default and can be
        revealed instantly or at some point after that. The miner has to
        save a reference to each hidden block it has created so that it can
        reveal them in the future.
        
        Parameters
        ----------
        
        block : blocksim.simulation.Block
            new block that has just been created with the miner as its owner.
            A reference to this block has to be saved for it to be published
            later on."""

        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):

        """This method is called when a miner chooses to publish a block so
        that it can delete its reference from its hidden blocks.
        
        Parameters
        ----------
        
        block : blocksim.simulation.Block
            published block to be removed from hidden blocks."""

        self.hidden_blocks.remove(block)

    def add_known_block(self, block):

        """This method is called when another miner informs the current miner of
        a hidden block that it has found so that the current miner is able to mine
        on top of it without it being revealed yet.
        
        Parameters
        ----------
        
        block : blocksim.simulation.Block
            hidden block that has been shown to the current miner."""

        self.known_blocks.append(block)

    def strat(self, struct):

        """This method is called when a miner has found a new block for the structure
        for it to choose its parent block. In other words, the miner has to choose
        on top of which block it will place its next found block. This method chooses
        a random block from the deepest blocks in the structure.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation containing the blockchain.
            
        Results
        -------
        
        block : blocksim.simulation.Block
            block on top of which the current miner will place its next found block"""

        return sample(struct.deep_blocks, 1)[0]

    def publish(self, struct, end=False):

        """This method is called when the state of the structure has changed and expects
        the miner to return the hidden blocks that it wants to publish in the form of
        a set. This miner publishes each block instantly.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation containing the blockchain.
        end : bool
            flag indicating whether the method is being called on update of the state
            or because the simulation is ending.
            
        Results
        -------
        
        blocks : set
            set containing the blocks that are to be published."""

        prev_blocks = self.hidden_blocks
        self.hidden_blocks = []
        return set(prev_blocks)

    def inform(self, struct, end=False):

        """This method is called when the state of the structure has changed
        and expects the miner to return a dictionary with the pairs
        ``miner_name: set()``, where the set contains the hidden blocks
        to be informed to the miner with name ``miner_name``. This miner
        doesn't use a communication strategy and it doesn't inform others
        of its blocks.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation containing the blockchain.
        end : bool
            flag indicating whether the method is being called on update of the
            state or because the simulation is ending.
            
        Results
        -------
        
        inform : dict
            dictionary with the pairs ``miner_name: set()``, where the set
            contains the hidden blocks to be informed to the miner with name
            ``miner_name``."""

        return dict()


class DefaultMiner(Miner):

    """Generate miner that uses the default strategy. When there is a tie in
    max depth, the algorithm chooses the branch that gives the current miner
    the max amount of payoff."""

    def strat(self, struct):

        """Choose a block to mine on top of. Choose the deepest block in the
        structure that belongs to the branch that maximizes the current miner's
        payoff.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation
            
        Results
        -------
        
        block : blocksim.simulation.Block
            chosen block to mine on top of"""

        next_blocks = struct.deep_blocks.copy()

        if len(next_blocks) > 1:
            while len(next_blocks) > 1:
                old_blocks = next_blocks
                next_blocks = set()
                for block in old_blocks:
                    next_blocks.add(block.parent)

            common_block = next_blocks.pop()
            block_payoff = {block: struct.payoff(block, common_block, struct.base)
                for block in struct.deep_blocks}

            for block in block_payoff:
                if self.name not in block_payoff[block]:
                    block_payoff[block][self.name] = {"block_number": 0, "payoff": 0}

            max_payoff = max(block_payoff, key=lambda x: block_payoff[x][self.name]["payoff"])
            max_payoff_blocks = set(filter(lambda x: block_payoff[x][self.name]["payoff"] == \
                block_payoff[max_payoff][self.name]["payoff"], struct.deep_blocks))
            sel_block = max_payoff_blocks.pop()
        else:
            sel_block = next_blocks.pop()

        return sel_block


class SelfishMiner(Miner):

    """Generate miner that uses the selfish strategy. Once the miner discovers
    a new block, they don't reveal it unless another branch catches up to its
    depth decremented by one. For example, if the hidden branch that the miner
    has created has a depth of ``n`` and there is another branch of depth
    ``n - 2``, the miner discloses every block that has a depth of ``n - 1``
    or less."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the miner"""

        super().__init__(name)
        self.just_forked = False
        self.first_block = None
        self.last_published = None

    def strat(self, struct):

        """Choose a block to mine on top of. Chooses the same way that the
        default strategy would, unless the miner has hidden blocks, in which
        case they mine on top of the last hidden block they have placed.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation
            
        Results
        -------
        
        block : blocksim.simulation.Block
            chosen block to mine on top of"""

        if self.hidden_blocks:
            return self.hidden_blocks[-1]
        
        next_blocks = struct.deep_blocks.copy()

        if self.last_published is not None and self.last_published.depth == struct.depth:
            if len(struct.deep_blocks) == 1:
                self.just_forked = True
            sel_block = self.last_published
        else:
            sel_block = next_blocks.pop()
            self.just_forked = True

        return sel_block

    def publish(self, struct, end=False):

        """Choose blocks to reveal. As explained in the documentation for
        ```SelfishMiner```, one only reveals a block if another branch has caught
        up with its depth decremented by one.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        pub_blocks : set
            set containing blocks to be revealed"""

        if end:
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = list(filter(lambda x: x.parent.is_hidden(), self.hidden_blocks))
            return set(filter(lambda x: not x.parent.is_hidden(), prev_blocks))

        if self.just_forked:
            self.just_forked = False
            self.first_block = self.hidden_blocks[-1]
            return set()
        elif self.hidden_blocks:
            if self.hidden_blocks == [self.first_block]:
                if self.first_block.depth == struct.depth:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = []
                    self.last_published = self.first_block
                    return set(prev_blocks)
                else:
                    return set()
            else:
                if self.hidden_blocks[-1].depth <= struct.depth + 1:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.is_hidden(), self.hidden_blocks))
                    publish = set(filter(lambda x: not x.parent.is_hidden(), prev_blocks))
                    self.last_published = max(publish, key=lambda x: x.depth)
                    return publish
                else:
                    prev_blocks = self.hidden_blocks
                    self.hidden_blocks = list(filter(lambda x: x.parent.is_hidden() or x.depth > struct.depth, self.hidden_blocks))
                    publish = set(filter(lambda x: not x.parent.is_hidden() and x.depth <= struct.depth, prev_blocks))
                    self.last_published = max(publish, default=self.last_published, key=lambda x: x.depth)
                    return publish
        else:
            return set()

class AlwaysForkMiner(Miner):

    """Generate miner that uses the always fork strategy. At first the
    miner mines on top of the genesis block. After that, they only mine on
    top of the last block they have placed in the structure."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the miner"""

        super().__init__(name)
        self.last_block = None

    def strat(self, struct):

        """Choose a block to mine on top of. Chooses the genesis block if
        the miner hasn't placed any blocks. Otherwise, chooses the last block
        placed by the miner.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation
            
        Results
        -------
        
        block : blocksim.simulation.Block
            chosen block to mine on top of"""

        if self.last_block:
            return self.last_block
        else:
            block = struct.deep_blocks.pop()
            struct.deep_blocks.add(block)
            return block

    def publish(self, struct, end=False):

        """Choose blocks to reveal. Reveal all hidden blocks.
        
        Parameters
        ----------
        
        struct : blocksim.simulation.Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        pub_blocks : set
            set containing blocks to be revealed"""

        if self.hidden_blocks:
            self.last_block = self.hidden_blocks[-1]
            prev_blocks = self.hidden_blocks
            self.hidden_blocks = []
            return set(prev_blocks)
        else:
            return set()
