import sys
sys.path.append(".")

from pwArgumentAgent import ArgumentAgent, ArgumentModel
from arguments.Argument import Argument

if __name__ == "__main__":
    argument_model = ArgumentModel()
    alice = ArgumentAgent(0, argument_model, "Alice")
    alice.generate_preferences([])
    argument = Argument(True, alice.item_list[0])
    print([crit for crit in argument.list_supporting_proposal("Electric Engine",  alice.get_preference())])
    print([crit for crit in argument.list_attacking_proposal("Electric Engine",  alice.get_preference())])