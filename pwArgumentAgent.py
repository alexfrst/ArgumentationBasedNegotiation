import random

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
        # diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        # electric_engine = Item("Electric Engine", "A very quiet engine")
        # self.item_list = [diesel_engine, electric_engine]

    def step(self):
        super().step()
        list_messages = self.get_new_messages()
        other = [agent.get_name() for agent in self.model.schedule.agents if agent.get_name() != self.get_name()][0]

        if len(list_messages) == 0 and self.get_name() == "Alice":
            self.send_message(Message(self.get_name(), other, MessagePerformative.PROPOSE,
                                      self.preference.most_preferred(self.item_list)))

        for message in list_messages:
            print(message)
            content = message.get_content()

            if message.get_performative() == MessagePerformative.PROPOSE:
                print("\n-----------------------------------------PROPOSE-----------------------------------------")

                if self.preference.is_item_among_top_10_percent(content, self.item_list):

                    if (content.get_name() == self.preference.most_preferred(self.item_list).get_name()):

                        self.send_message(
                            Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, content))

                    else:
                        print(
                            f"{self.get_name()} propose something else : {self.preference.most_preferred(self.item_list)}")
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.PROPOSE,
                                                  self.preference.most_preferred(self.item_list)))



                else:
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ASK_WHY, content))

            if message.get_performative() == MessagePerformative.ACCEPT:
                print("\n-----------------------------------------ACCEPT-----------------------------------------")
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, content))

            if message.get_performative() == MessagePerformative.COMMIT:
                print("\n-----------------------------------------COMMIT-----------------------------------------")
                if content.get_name() in [it.get_name() for it in self.item_list]:
                    self.item_list = list(filter(lambda x: x.get_name() != content.get_name(), self.item_list))
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, content))

            if message.get_performative() == MessagePerformative.ASK_WHY:
                print("\n-----------------------------------------ASK WHY-----------------------------------------")

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
                        print("On a pass")
                        pass
                else:
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ARGUE,(current_item,
                                              self.argument_parsing(self.support_proposal(current_item)))))
                    print(str(self.arguments['Electric Engine'].couple_values_list))

            if message.get_performative() == MessagePerformative.ARGUE:
                print("\n-----------------------------------------ARGUE-----------------------------------------")
                item, criterion_couple = content
                if self.is_argument_attack(item, criterion_couple):
                    if self.attack_argument(item) == None:
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, item))
                    else:
                        print("TODO")
                        #self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ARGUE, (item,)))
                else:
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, item))

                # TODO : implement the argument agent

    def get_preference(self):
        return self.preference

    def generate_preferences(self, item_list):
        df = pd.read_csv(f"data/{self.get_name()}.csv", index_col=0, sep=";")
        agent_pref = Preferences()
        agent_pref.set_criterion_name_list([CriterionName[col] for col in df.columns])
        items = []
        for index, data in df.iterrows():
            item = Item(index, "Awesome description")
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
        : return : Argument - the strongest supportive argument
        """

        if item not in self.arguments:
            argument = Argument(True, item)
            supportive_argument = argument.list_supporting_proposal(item, self.get_preference())
            for criterion, value in supportive_argument:
                argument.add_premiss_couple_values(criterion.name, value.name)
            self.arguments[item] = argument

        if len(self.arguments[item].couple_values_list) > 0:
            return self.arguments[item]

        return None

    def argument_parsing(self, argument):

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
        criterion, value = criterion_couple_values

        importance = self.preference.get_criterion_name_list().index(criterion)
        if importance > len(self.preference.get_criterion_name_list()) / 2:
            return False
        if value > self.preference.get_value(item, criterion):
            return False
        return True


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
    alice.generate_preferences([])
    argument_model.schedule.add(alice)


    bob = ArgumentAgent(1, argument_model, "Bob")
    bob.generate_preferences([])
    argument_model.schedule.add(bob)

# m1 = Message("Alice", "Bob", MessagePerformative.PROPOSE, "Tu veux manger ?")
    # m2 = Message("Bob", "Alice", MessagePerformative.ACCEPT, "Evidemment Bregs")
    #
    # alice.send_message(m1)
    # bob.send_message(m2)
    step = 0
    while step < 10:
        argument_model.step()
        step += 1

# To be completed
