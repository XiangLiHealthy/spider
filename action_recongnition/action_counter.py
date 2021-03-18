
class ActionCounter:
    def __init__(self):
        self.m_name = ''
        self.m_counter = 0

        return

    def addAction(self, name):
        if self.name != name:
            self.m_counter = 1
            self.m_name = name
        else:
            self.m_counter += 1

        return self