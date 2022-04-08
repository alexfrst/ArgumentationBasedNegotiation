#!/ usr/bin /env python3
import sys
import os

sys.path.append(".")

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from communication.preferences.Preferences import Preferences
from communication.preferences.Value import Value

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
        self.item = item if isinstance(item, str) else item.get_name()
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

    def list_supporting_proposal(self, item, preferences: Preferences):
        """
        Generate a list of premisses which can be used to support an item
        : param item : Item - name of the item
        : return : list of all premisses PRO an item ( sorted by order of importance
        based on agent 's preferences )
        """
        supporting_proposal = []

        for criterion in preferences.get_criterion_name_list():
            item_value = preferences.get_value(item, criterion)
            if item_value in [Value.GOOD, Value.VERY_GOOD]:
                supporting_proposal.append(criterion)
        return supporting_proposal

    def list_attacking_proposal(self, item, preferences: Preferences):
        """
        Generate a list of premisses which can be used to support an item
        : param item : Item - name of the item
        : return : list of all premisses PRO an item ( sorted by order of importance
        based on agent 's preferences )
        """
        supporting_proposal = []

        for criterion in preferences.get_criterion_name_list():
            item_value = preferences.get_value(item, criterion)
            if item_value in [Value.BAD, Value.VERY_BAD]:
                supporting_proposal.append(criterion)
        return supporting_proposal

