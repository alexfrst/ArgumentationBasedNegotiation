import random
import pandas as pd

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService
from communication.preferences.Preferences import Preferences, CriterionName, CriterionValue, Value
from communication.preferences.Item import Item


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent .
    """


    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)
        self.preference: Preferences = None
        self.__v = random.randint(0,1100)
        # diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        # electric_engine = Item("Electric Engine", "A very quiet engine")
        # self.item_list = [diesel_engine, electric_engine]

    def step(self):
        super().step()
        list_messages = self.get_new_messages()
        other = [agent.get_name() for agent in self.model.schedule.agents if agent.get_name() != self.get_name()][0]

        if len(list_messages)==0:
            self.send_message(Message(self.get_name(), other, MessagePerformative.PROPOSE, self.preference.most_preferred(self.item_list)))

        for message in list_messages:
            print(message)
            if message.get_performative() == MessagePerformative.PROPOSE:
                content = message.get_content()

                if self.preference.is_item_among_top_10_percent(content, self.item_list):

                    if (content.get_name() == self.preference.most_preferred(self.item_list).get_name()):

                        print(f"{self.get_name()} is accepting {content.get_name()}")
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ACCEPT, "Whith pleasure"))

                    else:
                        print(f"{self.get_name()} propose something else : {self.preference.most_preferred(self.item_list)}")
                        self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.PROPOSE, self.preference.most_preferred(self.item_list)))

                        

                else:
                    print(f"{self.get_name()} is rejecting {content.get_name()}")
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.ASK_WHY, "Why ?"))

            if message.get_performative() == MessagePerformative.ACCEPT:
                print(f"{self.get_name()} is commiting.")
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, "Well received"))

            if message.get_performative() == MessagePerformative.COMMIT:
                print(f"{self.get_name()} is commiting.")
                self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.COMMIT, "Well received 2"))



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
    while step < 3:
        argument_model.step()
        step += 1


# To be completed
