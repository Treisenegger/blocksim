"""Standard player strategies for conducting the experiments. Each player is generated
with a name that serves as its identificator. Also, each player has to have 6 methods
called ``add_hidden_block``, which saves a new hidden block created by the player,
``delete_hidden_block``, which deletes the reference to a hidden block created by the
player after revealing it, ``add_known_block``, which saves a hidden block created by
another player, ``strat``, which chooses a block to mine on top of, ``publish``,
which chooses blocks to reveal, and ``inform``, which chooses blocks to communicate
to other players."""

from random import sample

from .simulation import Block


class DefPlayerRandom:

    """Generate player that uses the default strategy but when there is a tie in
    max depth the algorithm chooses randomly between the deepest blocks to mine."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the player"""

        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []

    def add_hidden_block(self, block):

        """Save a hidden block created by current player.
        
        Parameters
        ----------
        
        block : Block
            new hidden block to be save"""

        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):

        """Delete reference to hidden block created by the current player after
        revealing it.
        
        Parameters
        ----------
        
        block : Block
            block to be forgotten"""

        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):

        """Save a hidden block created by another player.
        
        Parameters
        ----------
        
        block : Block
            block to be saved"""

        self.known_blocks.append(block)

    def strat(self, struct):

        """Choose a block to mine on top of. Choose a random block from the
        deepest blocks in the structure.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
            
        Results
        -------
        
        block : Block
            chosen block to mine on top of"""

        return sample(struct.deep_blocks, 1)[0]

    def publish(self, struct, end=False):

        """Choose blocks to reveal. Reveal all hidden blocks.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        pub_blocks : set
            set containing blocks to be revealed"""

        prev_blocks = self.hidden_blocks
        self.hidden_blocks = []
        return set(prev_blocks)

    def inform(self, struct, end=False):

        """Choose blocks to communicate to other players. Don't communicate any
        block.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        com_blocks : dict
            dictionary indicating which blocks to communicate to which players"""

        return dict()


class DefPlayer:

    """Generate player that uses the default strategy. When there is a tie in
    max depth, the algorithm chooses the branch that gives the current player
    the max amount of payoff."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the player"""

        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []

    def add_hidden_block(self, block):

        """Save a hidden block created by current player.
        
        Parameters
        ----------
        
        block : Block
            new hidden block to be save"""

        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):

        """Delete reference to hidden block created by the current player after
        revealing it.
        
        Parameters
        ----------
        
        block : Block
            block to be forgotten"""

        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):

        """Save a hidden block created by another player.
        
        Parameters
        ----------
        
        block : Block
            block to be saved"""

        self.known_blocks.append(block)

    def strat(self, struct):

        """Choose a block to mine on top of. Choose the deepest block in the
        structure that belongs to the branch that maximizes the current player's
        payoff.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
            
        Results
        -------
        
        block : Block
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

    def publish(self, struct, end=False):

        """Choose blocks to reveal. Reveal all hidden blocks.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        pub_blocks : set
            set containing blocks to be revealed"""

        prev_blocks = self.hidden_blocks
        self.hidden_blocks = []
        return set(prev_blocks)

    def inform(self, struct, end=False):

        """Choose blocks to communicate to other players. Don't communicate any
        block.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        com_blocks : dict
            dictionary indicating which blocks to communicate to which players"""

        return dict()


class SelfPlayer:

    """Generate player that uses the selfish strategy. Once the player discovers
    a new block, they don't reveal it unless another branch catches up to its
    depth decremented by one. For example, if the hidden branch that the player
    has created has a depth of ``n`` and there is another branch of depth
    ``n - 2``, the player discloses every block that has a depth of ``n - 1``
    or less."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the player"""

        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.just_forked = False
        self.first_block = None
        self.last_published = None

    def add_hidden_block(self, block):

        """Save a hidden block created by current player.
        
        Parameters
        ----------
        
        block : Block
            new hidden block to be save"""

        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):

        """Delete reference to hidden block created by the current player after
        revealing it.
        
        Parameters
        ----------
        
        block : Block
            block to be forgotten"""

        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):

        """Save a hidden block created by another player.
        
        Parameters
        ----------
        
        block : Block
            block to be saved"""

        self.known_blocks.append(block)

    def strat(self, struct):

        """Choose a block to mine on top of. Chooses the same way that the
        default strategy would, unless the player has hidden blocks, in which
        case they mine on top of the last hidden block they have placed.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
            
        Results
        -------
        
        block : Block
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
        SelfPlayer, one only reveals a block if another branch has caught
        up with its depth decremented by one.
        
        Parameters
        ----------
        
        struct : Structure
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

    def inform(self, struct, end=False):

        """Choose blocks to communicate to other players. Don't communicate any
        block.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        com_blocks : dict
            dictionary indicating which blocks to communicate to which players"""

        return dict()

class AFPlayer:

    """Generate player that uses the always fork strategy. At first the
    player mines on top of the genesis block. After that, they only mine on
    top of the last block they have placed in the structure."""

    def __init__(self, name):

        """Parameters
        ----------
        
        name : string
            identifier for the player"""

        self.name = name
        self.hidden_blocks = []
        self.known_blocks = []
        self.last_block = None

    def add_hidden_block(self, block):

        """Save a hidden block created by current player.
        
        Parameters
        ----------
        
        block : Block
            new hidden block to be save"""

        self.hidden_blocks.append(block)

    def delete_hidden_block(self, block):

        """Delete reference to hidden block created by the current player after
        revealing it.
        
        Parameters
        ----------
        
        block : Block
            block to be forgotten"""

        self.hidden_blocks.remove(block)
    
    def add_known_block(self, block):

        """Save a hidden block created by another player.
        
        Parameters
        ----------
        
        block : Block
            block to be saved"""

        self.known_blocks.append(block)

    def strat(self, struct):

        """Choose a block to mine on top of. Chooses the genesis block if
        the player hasn't placed any blocks. Otherwise, chooses the last block
        placed by the player.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
            
        Results
        -------
        
        block : Block
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
        
        struct : Structure
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

    def inform(self, struct, end=False):

        """Choose blocks to communicate to other players. Don't communicate any
        block.
        
        Parameters
        ----------
        
        struct : Structure
            data structure of the simulation
        end : bool
            flag indicating whether the method is being called after the
            simulation has ended or before that
            
        Results
        -------
        
        com_blocks : dict
            dictionary indicating which blocks to communicate to which players"""

        return dict()
