
class Action:
    def __init(self):
        self.m_name = ''
        self.m_action_time = 0.0
        self.m_start_time = 0.0
        self.m_end_time = 0.0
        self.m_pose_angles = []
        self.m_pose_landmark = []
        self.m_match_times = 0
        self.m_need_times = 0xfffffffff

    def match(self, angles):

        return