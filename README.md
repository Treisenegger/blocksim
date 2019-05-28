# BlockSim

BlockSim is a Python library for conducting simulations to test the efficiency of different mining strategies on the Bitcoin structure.

## Dependencies

To install the dependencies needed for running BlockSim, run the command

```pip install -r requirements.txt```

## Miner example

In this section we give an example of a miner implementation. This miner will implement a strategy through which it will fork only if the deepest blocks in the structure are at most two levels deeper than its last placed block. Otherwise, it will randomly mine on top of one of the deepest blocks in the structure. Also, it will publish every block instantly and will neither communicate the existence of hidden blocks nor use any blocks it is informed of.

```python
class ForkTwoDistanceMiner(Miner):
    
```

## Running the simulation

