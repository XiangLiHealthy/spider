class ActionScore:
    def __init(self):

        return

    def caculateAngleScore(self, possible_action):

        return 70

    def caculateSpeedScore(self, possible_action):

        return 30

    def getScore(self, possible_action):
        # the score of pose_angle
        angle_score = self.caculateAngleScore(possible_action)

        # the score of action time
        speed_score = self.caculateSpeedScore(possible_action)

        # the score of pose keep time

        # weighted average score

        return angle_score * 0.8 + speed_score * 0.2
