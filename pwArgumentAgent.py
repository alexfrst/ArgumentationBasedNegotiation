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
from communication.preferences.Preferences import Preferences, CriterionName, CriterionValue, Value


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent .
    """

    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.preference: Preferences = None
        self.__v = random.randint(0, 1100)
        self.arguments: dict[str,Argument] = {}
        self.counter_arguments = {}
        self.already_proposed = []
        self.number_commit = 0

    def step(self):
        super().step()
        list_messages = self.get_new_messages()
        other = [agent.get_name() for agent in self.model.schedule.agents if agent.get_name() != self.get_name()][0]

        if len(list_messages) == 0 and self.get_name() == "Alice":
            self.send_message(Message(self.get_name(), other, MessagePerformative.PROPOSE,
                                      self.preference.most_preferred(self.item_list)))

        for message in list_messages:

            print(message)
            content = message.get_content() #content of the message

            if message.get_performative() == MessagePerformative.PROPOSE:
                self.handle_propose(message, content)

            if message.get_performative() == MessagePerformative.ACCEPT:
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, content))

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
                agent_pref.add_criterion_value(CriterionValue(item, CriterionName[row[0]], Value[row[1]]))
        self.item_list = items
        self.preference = agent_pref
        return items, agent_pref

    def support_proposal(self, item):
        """
        Used when the agent receives " ASK_WHY " after having proposed an item
        : param item : str - name of the item which was proposed
        : return : Argument - an argument object which contains the list of all the arguments available to defend the given item
        """

        #if we never created argument for this item, we create it
        if item not in self.arguments:
            argument = Argument(True, item)
            supportive_argument = argument.list_supporting_proposal(item, self.get_preference())
            for criterion, value in supportive_argument:
                argument.add_premiss_couple_values(criterion.name, value.name)
            self.arguments[item] = argument

        #if we still have arguments left in our list 
        if len(self.arguments[item].couple_values_list) > 0:
            return self.arguments[item]

        return None

    def argument_parsing(self, argument:Argument):
        """Parse an argument and return the strongest one"""

        #if it's a counter argument
        if argument.boolean_decision == False:
            criterion = self.counter_arguments[argument.item].couple_values_list.pop(0)
        else:
            criterion = self.arguments[argument.item].couple_values_list.pop(0)

        #print(f"{self.arguments[argument.item][0].item}==>{criterion.criterion_name} = {criterion.value}")

        return (criterion.criterion_name, criterion.value)

    def attack_argument(self, item, criterion_couple_values):

        if item not in self.counter_arguments:
            argument = Argument(False, item)
            unsupported_argument = argument.list_attacking_proposal(item, self.get_preference())
            for criterion, value in unsupported_argument:
                argument.add_premiss_couple_values(criterion.name, value.name)
            self.counter_arguments[item] = argument

        if len(self.counter_arguments[item].couple_values_list) > 0:

            return self.counter_arguments[item]

        return None

    def is_argument_attack(self, item, criterion_couple_values):
        """Boolean which indicates if an argument can be attacked or not and fill the counter arguments"""
        criterion, value = criterion_couple_values

        importance = [crit.name for crit in self.preference.get_criterion_name_list()].index(criterion)
        #if the criterion is not important for him (not in the 50% preferred criterion)
        if importance > len(self.preference.get_criterion_name_list()) / 2:
            return False

        #if its value for the given criterion is less than the one of the agent
        if Value[value].value > self.preference.get_value(item, CriterionName[criterion]).value:
            return False
        return True


    def handle_propose(self, message, content):
        """Handle the messages of type PROPOSE"""

        #if the proposed item is among the top 10 percent of the agent who receives the proposal
        if self.preference.is_item_among_top_10_percent(content, self.item_list):

            #if the proposed item is the favorite item of the agent who receives the proposal -> he accepts the item
            if (content.get_name() == self.preference.most_preferred(self.item_list).get_name()):

                self.send_message(
                    Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, content))

            #else he proposes something else
            else:
                print(f"{self.get_name()} propose something else : {self.preference.most_preferred(self.item_list)}")
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.PROPOSE,
                                            self.preference.most_preferred(self.item_list)))

        else:
            self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ASK_WHY, content))

    def handle_commit(self, message, content):
        """Handle the messages of type COMMIT"""

        item_name = content if isinstance(content,str) else content.get_name()
        if item_name in [it.get_name() for it in self.item_list]:
            self.item_list = list(filter(lambda x: x.get_name() != item_name, self.item_list))
        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, content))
        self.number_commit +=1

        #if both the agents commited, we end the negotiation
        if self.number_commit == 2:
            print(f"\nEnd of the negociation ! The agents agreed on the item : {item_name}")
            sys.exit()

    def handle_askwhy(self, message, content):
        """Handle the messages of type ASK_WHY"""

        current_item = [item for item in self.item_list if item.get_name() == content.get_name()][0].get_name()
        if self.support_proposal(current_item) == None:
            print(
                f"{self.get_name()} propose something else: {self.preference.most_preferred(self.item_list)}")
            unproposed_best_items = [item for item in self.preference.get_item_sorted_by_score(self.item_list)
                                        if item not in self.already_proposed]
            if len(unproposed_best_items) > 0:
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.PROPOSE,
                                            unproposed_best_items[0]))
            else:
                pass
        else:
            self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ARGUE,(current_item,
                                        self.argument_parsing(self.support_proposal(current_item)))))
            print(str(self.arguments['Electric Engine'].couple_values_list))

    def handle_argue(self, message, content):
        """Handle the messages of type ARGUE"""
        item, criterion_couple = content

        #if the argument can be attacked by the agent
        if self.is_argument_attack(item, criterion_couple):
            #if we don't have counter arguments -> we accept the item
            if self.attack_argument(item, criterion_couple) == None:
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, item))
            #we give a counter argument
            else:
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ARGUE, (item, self.argument_parsing(self.attack_argument(item, criterion_couple)))))
        
        #the argument can't be attacked by the agent -> he accepts
        else:
            self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, item))



class ArgumentModel(Model):
    """
    ArgumentModel which inherit from Model .
    """

    def __init__(self):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        # To be completed
        #
        # a = ArgumentAgent (id , " agent_name ")
        # a. generate_preferences ( preferences )
        # self . schedule .add(a)
        # ...

        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()


if __name__ == '__main__':
    # Init the model and the agents
    argument_model = ArgumentModel()
    MessageService.get_instance().set_instant_delivery(True)

    alice = ArgumentAgent(0, argument_model, "Alice")
    alice.generate_preferences()
    argument_model.schedule.add(alice)


    bob = ArgumentAgent(1, argument_model, "Bob")
    bob.generate_preferences()
    argument_model.schedule.add(bob)

    step = 0
    while step < 10:
        print("step=",step)
        argument_model.step()
        step += 1
