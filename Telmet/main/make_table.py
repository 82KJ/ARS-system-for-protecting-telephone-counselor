from .model_control import ModelControl

class ResultTable:
    def __init__(self):
        self.model_control = ModelControl()
        self.all_conversation = self.model_control.select_all_conversation()
        self.list_of_table = list()
        self.make_list()

    def make_list(self):
        conversation = list(self.all_conversation)
        
        dict_conversation = dict()
        idx = 1
        result_match = ["Normal", "Abuse", "Sexual"]
        for conv in conversation:
            dict_conversation["Num"] = idx
            dict_conversation["Time"] = str(conv.time.time())[:-7]
            dict_conversation["Content"] = conv.content
            dict_conversation["Result"] = result_match[conv.result]
            self.list_of_table.append(dict_conversation)

            idx += 1
            dict_conversation = dict()

    def get_table(self):
        return self.list_of_table