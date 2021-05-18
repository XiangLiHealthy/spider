from train_solution import TrainSolution

class CommandHandler :
    def __init__(self):

        return

    def perform(self, task, landmarks):

        return


class PrepareCommandImp(CommandHandler) :
    def __init__(self):

        return

    def perform(self, task, landmarks):

        return


class TrainCommandImp(CommandHandler):
    def __init__(self):
        self.train_ = TrainSolution()

        return

    def perform(self, task, landmarks):
        return self.train_.perform(task, landmarks)


class EvaluationCommandImp(CommandHandler):
    def __init__(self):
        return

    def perform(self, task, landmarks):
        return


