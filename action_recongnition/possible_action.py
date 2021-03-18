from action import Action

class PossibleAction:
    def __init__(self):
        self.m_action = Action()
        self.m_pose_angles = []
        self.m_first_matched_time = 0.0
        self.m_finished_matched_time = 0.0

        return
