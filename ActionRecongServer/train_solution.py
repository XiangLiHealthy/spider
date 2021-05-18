from util import Util
from uri_def import *
from enum import Enum
from math import pow

TRAINING_DOING = 'doing'
TRAINING_OK = 'finish'
THRESHOLD = 300
REVERT_THRESHOLD = 3

class MatchContext:
    def __init__(self):
        self.teacher_poses = None
        self.user_pose = None
        self.matched_idx = -1


class TrainSolution :
    def __init__(self):

        return

    def get_move_direction(self, context, current_idx):
        teacher = context.teacher

        # if up and down is marked,direction is revert
        current_pose = context.teacher.poses[current_idx]
        direction = MOVE_DIRECTION.UP

        try:
            while True :
                if 1 == current_pose.up and 1 == current_pose.down :
                    direction = MOVE_DIRECTION.REVERT
                    break

                # if idx is bigger than last idx ,direction is up
                if teacher.last_idx < current_idx :
                    direction = MOVE_DIRECTION.UP
                    break

                # if idx is smaller than last idx, dirction is down
                elif teacher.last_idx > current_idx :
                    direction = MOVE_DIRECTION.DOWN
                    break

                else :
                    direction = teacher.last_direction
                    break

            teacher.last_direction = direction
            teacher.last_idx = current_idx
        except Exception as e :
            print ('get move direction except :{}'.format(e))

        return direction

    def match_teacher(self, context):
        state = False
        idx = 0

        try:
            teacher_poses = context.teacher.poses
            user_angles = context.user_pose
            for one_pose in teacher_poses :
                teacher_angles = one_pose.angles
                diff = Util.caculatePoseDifference(teacher_angles, user_angles)
                if diff < THRESHOLD :
                    state = True
                    context.matched_idx = idx

                    move_direction = self.get_move_direction(context, idx)
                    if MOVE_DIRECTION.UP == move_direction :
                        one_pose.up = 1
                        one_pose.up_diff = diff
                    elif MOVE_DIRECTION.DOWN == move_direction :
                        one_pose.down = 1
                        one_pose.down_diff = 1
                    elif move_direction == MOVE_DIRECTION.REVERT:
                        context.teacher.rever_count += 1
                        one_pose.revert_diff =  diff
                        one_pose.revert_idx = idx

                    break

                idx += 1
        except Exception as e :
            print ('match teacher except :{}'.format(e))

        return state

    def tips_error(self, context):

        return ''

    # case1:match rate is upper threshold and tread is download and download is over
    # case2: up and down rate is upon of 1/3 and move trend is shutdown
    def check_match_rate(self, context):
        if context.teacher.rever_count > REVERT_THRESHOLD :
            return True

        return False

    def score(self, context):
        score = 0

        try:
            teacher = context.teacher

            # get matched rate score
            matched_count = 0
            sum_diff = 0
            for one_pose in teacher.poses :
                if 1 == one_pose.up :
                    matched_count += 1
                if 1 == one_pose.down :
                    matched_count += 1

                sum_diff += pow(one_pose.up_diff, 2)+ pow(one_pose.down_diff , 2)

            teacher_count = len(teacher.poses)
            rate_score = int(matched_count / teacher_count * 100)

            # get diff score
            average_diff = sum_diff / matched_count
            standard = pow(THRESHOLD, 2)

            diff_score = int ( (standard - average_diff) / standard * 100 )

            # get action time score

            score = rate_score * 0.8 + diff_score * 0.2
        except Exception as e :
            print ('score except :{}'.format(e))

        return score

    def keep_time(self, context):

        return 0

    def clear_match_state(self, context):
        try:
            teacher = context.teacher
            # clear last_idx and last direction

            # clear matched mark and diff
            for one_pose in teacher.poses :
                one_pose.up = 0
                one_pose.down = 0
                one_pose.up_diff = 0
                one_pose.down_diff = 0

                if teacher.last_direction == MOVE_DIRECTION.UP :
                    one_pose.up = one_pose.revert_idx
                    one_pose.up_diff = one_pose.revert_diff
                else :
                    one_pose.down = one_pose.revert_idx
                    one_pose.down_diff = one_pose.revert_diff

            # clear revert count
            teacher.revert_count = 0
        except Exception as e :
            print ('clear match state except :{}'.format(e))

        return None

    def perform(self, task, landmarks):
        j_response = {}
        j_response['result'] = RESULTl_OK
        j_response['desc'] = ''

        try:
            data = {}
            data['state'] = TRAINING_DOING
            data['score'] = 0
            data['count'] = 0
            data['error_tip'] = ''
            data['time_keep'] = 5

            context = MatchContext()

            # get pose angle
            while True :
                context.teacher = task.config
                context.user_pose = Util.translateLandmarks(landmarks)

                # match teacher
                state = self.match_teacher(context)
                if state is False:
                    data['error_tips'] = self.tips_error(context)
                    break

                data['time_keep'] = self.keep_time(context)

                # check match rate
                if False == self.check_match_rate(context) :
                    break

                # score
                data['score'] = self.score(context)
                self.clear_match_state(context)

                task.count += 1
                data['count'] = task.count

                if task.count >= task.need_count :
                    data['state'] = TRAINING_OK

                break

            j_response['data'] = data
        except Exception as e :
            print ('train perform except :{}'.format(e))
            j_response['result'] = RESULT_FAILD

        return j_response