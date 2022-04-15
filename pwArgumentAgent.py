import random
import sys

import pandas as pd
from mesa import Model
from mesa.time import RandomActivation

from arguments.Argument import Argument
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService
from communication.preferences.Item import Item
from communication.preferences.Preferences import (
    Preferences,
    CriterionName,
    CriterionValue,
    Value,
)

verbose = True

def log(*args):
    if verbose == True:
        print(*args)

class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent .
    """

    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.preference: Preferences = None
        self.__v = random.randint(0, 1100)
        self.arguments: dict[str, Argument] = {}
        self.counter_arguments = {}
        self.already_proposed = []
        self.number_commit = 0
        self.winning_item = ""

    def step(self):
        super().step()
        list_messages = self.get_new_messages()
        other = [
            agent.get_name()
            for agent in self.model.schedule.agents
            if agent.get_name() != self.get_name()
        ][0]

        for message in list_messages:

            log(message)
            content = message.get_content()  # content of the message

            if message.get_performative() == MessagePerformative.PROPOSE:
                self.handle_propose(message, content)

            if message.get_performative() == MessagePerformative.ACCEPT:
                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.COMMIT,
                        content,
                    )
                )
                self.item_list = [item for item in self.item_list if item.get_name() != content ]

            if message.get_performative() == MessagePerformative.COMMIT:
                self.handle_commit(message, content)

            if message.get_performative() == MessagePerformative.ASK_WHY:
                self.handle_askwhy(message, content)

            if message.get_performative() == MessagePerformative.ARGUE:
                self.handle_argue(message, content)

    def get_preference(self):
        return self.preference

    def generate_preferences(self):
        """Generate the preferences of an agent given a CSV file containing the value associated for each criterion on an item"""
        df = pd.read_csv(f"data/{self.get_name()}.csv", index_col=0, sep=";")
        agent_pref = Preferences()
        agent_pref.set_criterion_name_list([CriterionName[col] for col in df.columns])
        items = []
        for index, data in df.iterrows():
            item = Item(index, "")
            items.append(item)

            for row in data.iteritems():
                agent_pref.add_criterion_value(
                    CriterionValue(item, CriterionName[row[0]], Value[row[1]])
                )
        self.item_list = items
        self.preference = agent_pref
        return items, agent_pref

    def support_proposal(self, item):
        """
        Used when the agent receives " ASK_WHY " after having proposed an item
        : param item : str - name of the item which was proposed
        : return : Argument - the best argument to defend the given item
        """

        # if we never created arguments for this item, we create them
        if item not in self.arguments:

            global_argument = Argument(True, item)
            #We create the list of supportive arguments for the given item
            supportive_argument = global_argument.list_supporting_proposal(
                item, self.get_preference()
            )
            self.arguments[item] = []
            for criterion, value in supportive_argument:
                argument = Argument(True, item)
                argument.comparison_list = []
                argument.add_premiss_couple_values(criterion.name, value.name)
                self.arguments[item].append(argument)

        #We still have arguments for the given item
        if len(self.arguments[item])>0:
            best_argument = self.arguments[item].pop(0)
            return best_argument

        return None

    def argument_parsing(self, argument: Argument):
        """Parse an argument"""

        return argument.item, argument.boolean_decision, argument.couple_values_list, argument.comparison_list

    def attack_argument(self, argument):
        item = argument[0]

        #If no counter arguments exist against the given argument, we create them
        if item not in self.counter_arguments:

            global_argument = Argument(False, item)
            unsupported_argument = global_argument.list_attacking_proposal(
                item, self.get_preference()
            )
            self.counter_arguments[item] = []
            for criterion, value in unsupported_argument:
                argument = Argument(False, item)
                argument.add_premiss_couple_values(criterion.name, value.name)
                argument.comparison_list=[]
                self.counter_arguments[item].append(argument)

        if len(self.counter_arguments[item]) > 0:
            best_argument = self.counter_arguments[item].pop(0)
            return best_argument

        return None

    def is_argument_attack(self, argument):
        """Boolean which indicates if an argument can be attacked or not and fill the counter arguments"""
        item, boolean_decision, criterion_couple, criterion_comparison = argument
        criterion = criterion_couple[0].criterion_name
        value = criterion_couple[0].value

        importance = [
            crit.name for crit in self.preference.get_criterion_name_list()
        ].index(criterion)
        # if the criterion is not important for him (not in the 50% preferred criterion)
        if importance > len(self.preference.get_criterion_name_list()) / 2:
            return True

        # if its value for the given criterion is less than the one of the agent
        if (
                Value[value].value
                > self.preference.get_value(item, CriterionName[criterion]).value
        ):
            return True
        return False

    def handle_propose(self, message, content):
        """Handle the messages of type PROPOSE"""

        # if the proposed item is among the top 10 percent of the agent who receives the proposal
        if self.preference.is_item_among_top_10_percent(content, self.item_list):

            # if the proposed item is the favorite item of the agent who receives the proposal -> he accepts the item
            if (
                    content.get_name()
                    == self.preference.most_preferred(self.item_list).get_name()
            ):

                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.ACCEPT,
                        content,
                    )
                )

            # else he proposes something else
            else:
                log(
                    f"{self.get_name()} propose something else : {self.preference.most_preferred(self.item_list)}"
                )
                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.PROPOSE,
                        self.preference.most_preferred(self.item_list),
                    )
                )

        else:
            self.send_message(
                Message(
                    self.get_name(),
                    message.get_exp(),
                    MessagePerformative.ASK_WHY,
                    content,
                )
            )

    def handle_commit(self, message, content):
        """Handle the messages of type COMMIT"""

        item_name = content if isinstance(content, str) else content.get_name()
        self.winning_item = content
        if item_name in [it.get_name() for it in self.item_list]:
            self.item_list = list(
                filter(lambda x: x.get_name() != item_name, self.item_list)
            )
            self.send_message(
                Message(
                    self.get_name(), message.get_exp(), MessagePerformative.COMMIT, content
                )
            )
        else:
            log(
                f"\nEnd of the negociation ! The agents agreed on the item : {item_name}"
            )
            self.model.termination = True

    def handle_askwhy(self, message, content):
        """Handle the messages of type ASK_WHY"""

        current_item = [
            item for item in self.item_list if item.get_name() == content.get_name()
        ][0].get_name()
        if self.support_proposal(current_item) == None:
            log(
                f"{self.get_name()} propose something else: {self.preference.most_preferred(self.item_list)}"
            )
            unproposed_best_items = [
                item
                for item in self.preference.get_item_sorted_by_score(self.item_list)
                if item not in self.already_proposed
            ]
            if len(unproposed_best_items) > 0:
                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.PROPOSE,
                        unproposed_best_items[0],
                    )
                )
            else:
                pass
        else:
            self.send_message(
                Message(
                    self.get_name(),
                    message.get_exp(),
                    MessagePerformative.ARGUE,
                    self.argument_parsing(self.support_proposal(current_item)
                    ),
                )
            )

    def handle_argue(self, message, content):
        """Handle the messages of type ARGUE"""

        #item, boolean_decision, criterion_couple, criterion_comparison = content
        argument = content

        # if the argument can be attacked by the agent
        if self.is_argument_attack(argument):
            # if we don't have counter arguments -> we accept the item
            if self.attack_argument(argument) == None:
                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.ACCEPT,
                        argument[0],
                    )
                )
            # we give a counter argument
            else:
                if argument[1] == False:
                    #If it was a for argument, we give a counter argument
                    response = self.argument_parsing(self.support_proposal(argument[0]))
                else:
                    response = self.argument_parsing(self.attack_argument(argument))

                self.send_message(
                    Message(
                        self.get_name(),
                        message.get_exp(),
                        MessagePerformative.ARGUE,
                        response,
                    )
                )

        # the argument can't be attacked by the agent -> he accepts
        else:
            self.send_message(
                Message(
                    self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, argument[0]
                )
            )


class ArgumentModel(Model):
    """
    ArgumentModel which inherit from Model .
    """

    def __init__(self, name1, name2):
        self.termination = False
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        MessageService.get_instance().set_instant_delivery(True)

        alice = ArgumentAgent(0, self, name1)
        alice.generate_preferences()
        self.schedule.add(alice)

        bob = ArgumentAgent(1, self, name2)
        bob.generate_preferences()
        self.schedule.add(bob)
        self.steps = 0
        self.name1 = name1
        self.name2 = name2

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()
        if self.steps == 0:
            first_agent = self.schedule.agents[0]
            second_agent = self.schedule.agents[1]

            first_agent.send_message(
                Message(
                    first_agent.get_name(),
                    second_agent.get_name(),
                    MessagePerformative.PROPOSE,
                    first_agent.preference.most_preferred(first_agent.item_list),
                )
            )
            self.running = False

        self.steps += 1


if __name__ == "__main__":
    # Init the model and the agents
    first_player = "Bob"
    second_player = "Alice"
    if len(sys.argv) > 1:
        first_player = sys.argv[1]
        second_player = sys.argv[2]
        verbose = False


    model = ArgumentModel(first_player, second_player)

    first_agent = model.schedule.agents[0]
    most_prefered = first_agent.preference.most_preferred(first_agent.item_list).get_name()

    step = 0
    while step < 10:
        model.step()
        if model.termination:
            break
        step += 1

    while not model.termination:
        model.step()
    is_win = first_agent.winning_item == most_prefered

    if len(sys.argv) > 1:
        file = open("figures/results.csv", "a")
        file.write(f"{first_player},{second_player},{is_win},{most_prefered}\n")
