"""Standard payoff functions for conducting the experiments. Each function receives
a starting block and an ending block and returns the payoff corresponding to each player
for the branch between both blocks. The ``start_block`` is the deepest block in the
branch and the ``end_block`` is the shallowest."""

def constant_payoff(start_block, end_block, base):

    """Payoff function that assigns a constant value for each block in the
    branch that exists between ``start_block`` and ``end_block``, including
    both ends.
    
    Parameters
    ----------
    
    start_block : Block
        deepest block in the branch
    end_block : Block
        shallowest block in the branch
    base : Block
        root of the structure. Used if ``start_block`` and ``end_block``
        are not on the same branch as an ending condition for the calculation
        
    Results
    -------
    
    payoff_dict : dict
        dictionary that contains the information regarding payoff and number
        of blocks owned by each player in the branch"""

    payoff_dict = {}
    
    block = start_block

    while (block != end_block) and (block != base):
        if block.owner.name not in payoff_dict:
            payoff_dict[block.owner.name] = {"block_number": 0, "payoff": 0}
        payoff_dict[block.owner.name]["block_number"] += 1
        payoff_dict[block.owner.name]["payoff"] += 1
        block = block.parent

    return payoff_dict

def alpha_beta_payoff(alpha, beta):

    """Payoff function factory. This function creates a payoff function using the
    given parameters.
    
    Parameters
    ----------
    
    alpha : float
        number that accounts for the devaluation of money over time
    beta : float
        number that accounts for the diminishment of the payoff for each block in
        the Bitcoin structure after a certain amount of blocks have been created
        
    Results
    -------
    
    ab_payoff : function
        payoff function that uses the given parameters for the described
        purposes"""

    def ab_payoff(start_block, end_block, base):

        """Payoff function that assigns a value for each block in the
        branch that exists between ``start_block`` and ``end_block``,
        including both ends accounting for devaulation of money and
        diminishment of payoff in the Bitcoin structure over time.
        
        Parameters
        ----------
        
        start_block : Block
            deepest block in the branch
        end_block : Block
            shallowest block in the branch
        base : Block
            root of the structure. Used if ``start_block`` and ``end_block``
            are not on the same branch as an ending condition for the calculation
            
        Results
        -------
        
        payoff_dict : dict
            dictionary that contains the information regarding payoff and number
            of blocks owned by each player in the branch"""

        payoff_dict = {}
        
        block = start_block

        while (block != end_block) and (block != base):
            if block.owner.name not in payoff_dict:
                payoff_dict[block.owner.name] = {"block_number": 0, "payoff": 0}
            payoff_dict[block.owner.name]["block_number"] += 1
            payoff_dict[block.owner.name]["payoff"] += (alpha**block.tstamp)*(beta**block.depth)
            block = block.parent

        return payoff_dict
    return ab_payoff