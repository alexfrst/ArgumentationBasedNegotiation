#!/ usr/bin /env python3

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue


class Argument:
    """Argument class .
    This class implements an argument used in the negotiation .

    attr :
        decision :
        item :
        comparison_list :
        couple_values_list :
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument ."""
        # To be completed
        self.boolean_decision = boolean_decision
        self.item = item.get_name()
        self.comparison_list = []
        self.couple_values_list = []
        self.list_of_arguments = self.comparison_list.append(self.couple_values_list)
        self.argument = (self.item, self.comparison_list, self.list_of_arguments)

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list ."""
        # To be completed
        self.comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list ."""
        # To be completed
        self.couple_values_list.append(CoupleValue(criterion_name, value))
