
class Action:
    def __init__(self):
        self.m_name = ''
        self.m_action_time = 0.0
        self.m_actual_time = 0.0
        self.m_pose_angles = []
        self.m_teacher_pose = None
        self.m_match_times = 0
        self.m_need_times = 0xfffffffff
        self.m_current_pose_idx = 0
        self.m_en_name = ''
        self.video_path = ''
        self.angles_range = {}
        self.count = 0

    def match(self, angles):

        return