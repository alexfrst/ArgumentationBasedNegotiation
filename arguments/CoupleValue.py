#!/ usr/bin /env python3


class CoupleValue:
    """CoupleValue class .
    This class implements a couple value used in argument object .

    attr :
        criterion_name :
        value :
    """

    def __init__(self, criterion_name, value):
        """Creates a new couple value ."""
        # To be completed
        self.criterion_name = criterion_name
        self.value = value

    def __repr__(self):
        """Returns the string representation of the couple value ."""
        return "(" + self.criterion_name + ":" + str(self.value) + ")"
