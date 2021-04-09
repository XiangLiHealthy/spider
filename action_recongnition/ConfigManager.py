import json
import action

class ConfigManager :
    def __init__(self):
        try:
            self.m_j_action = ''
            self.STATE_NEED = 'need'
            self.STATE_FINISH = 'finish'
            self.TRAIN_OK = 'ok'
            self.TRAIN_DOING = 'doing'
            self.TEACH_NEED = 'nedd'
            self.TEACH_FINISH = "finish"

        except Exception as e :
            print ('config manager init error:{}'.format(e))

        return
    def loadActionModel(self):

        return

    def loadRecord(self):

        return

    def getEvaluationState(self):

        return

    def setEvaluationState(self):

        return

    def getTrainActions(self):

        return

    def getTeacherActions(self, name):

        return

    def getTeachState(self):

        return

    def getAllActions(self):

        return

g_config = ConfigManager()

