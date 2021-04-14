import cv2

from EvaluationModel import EvaluationModel
from enum import Enum
from ConfigManager import g_config
from util import Util
import time
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.platypus import SimpleDocTemplate, Paragraph

import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
import seaborn as sns
class EvaluationState(Enum):
    INIT = 0
    TEACHING = -1
    PREPARE = 1
    EVALUATING = 2
    KEEP_POSE = 3
    COMPLETE = 4
    NEXT = 5
    CREATE_REPORT = 6


class Teaching:
    def __init__(self, context):
        self.context_ = EvaluationModel()  # context
        self.video_idx_ = 0
        self.play_times_ = 0
        self.video_path_ = ''

        return

    def setImage(self):
        if self.video_path_ != self.context_.current_task_.j_config_['video_path']:
            self.video_path_ = self.context_.current_task_.j_config_['video_path']
            self.video_idx_ = 0
            self.play_times_ = 0
            self.context_.video_manager_.setVideo(self.video_path_)

        self.context_.evaluation_image_ = self.context_.video_manager_.getFrameByIdx(self.video_idx_)
        self.video_idx_idx_ += 1

        return

    def showTips(self, user_imnage):
        # where can L get tips content
        tips = ''

        point = (40, 40)
        cv2.putText(self.context_.evaluation_image_, tips, point, cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)

        return

    def perform(self, user_landmarks, user_image):
        # 1.play video
        self.setImage()

        # 2.tips text
        self.showTips(user_image)

        # increament times if play ok
        if self.context_.video_manager_.getFrameCount() == self.video_idx_:
            self.play_times_ += 1
            self.video_idx_ = 0

        # return next state if times ok
        state = EvaluationState.TEACHING
        if self.context_.current_task_.j_config_['play_times'] <= self.play_times_:
            state = EvaluationState.PREPARE

        return state


class Prepare:
    def __init__(self, context):
        self.teacher_image_ = None
        self.context_ = EvaluationModel()  # context
        self.pose_idx_ = 0

        return

    def setTeacherPose(self):
        # 1. get first pose landmarks and image
        pose = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]

        # 2.
        idx = pose['frame_num']
        self.context_.current_task_.teacher_image_ = self.context_.video_manager_.getFrameByIdx(idx)
        self.context_.video_manager_.release()
        self.context_.current_task_.teacher_landmarks = pose['landmarks']

        return

    def drawTeacherTips(self):
        tips = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]['tips']

        point = (40, 40)
        cv2.putText(self.context_.evaluation_image_, tips, point, cv2.FONT_HERSHEY_PLAIN, 2.0,
                    (0, 0, 255), 2)

        return

    def perform(self, user_landmarks, user_image):
        # 1.set teacher pose
        self.setTeacherPose()

        # 2. show teacher tips
        self.drawTeacherTips()

        # 3. recong user pose
        error_angles = Util.calculateAngleDiff(user_landmarks, user_image,
          self.context_.current_task_.teacher_landmarks, self.teacher_image_)

        # 4. error tips
        Util.pointErrorAngle(error_angles, user_landmarks, user_image)

        # 5. change state
        state = EvaluationState.PREPARE
        if 0 == len(error_angles):
            state = EvaluationState.EVALUATING

        return state


class Evaluating(Prepare):
    def __init__(self, context):
        super().__init__()

        return

    def initPoseIdx(self):
        # 1.get evaluation position
        position = super().context_.current_task_.j_config_['target_ability']

        # 2. get teacher pose num
        pose_num = len(super().context_.teacher_action_.m_teacher_pose)

        # 3. calculate pose idx
        super().pose_idx_ = int(pose_num * position)
        self.context_.current_task_.teacher_pose_idx_ = super().pose_idx_

        return

    def perform(self, user_landmarks, user_image):
        # 1.init pose idx
        self.initPoseIdx()

        # 2.set teacher pose
        super().setTeacherPose()

        # 3. show teaacher tips
        super().drawTeacherTips()

        # 4. change state
        return EvaluationState.KEEP_POSE


class Keeping:
    def __init__(self, context):
        self.keep_time_start_ = 0
        self.last_user_pose = []

        self.KEEP_START = 1
        self.KEEP_OVER = 5

        return

    def perform(self, user_landmarks, user_image):
        state = EvaluationState.KEEP_POSE
        if len(self.last_user_pose) == 0:
            self.last_user_pose = user_landmarks
            return state

        error_angles = Util.calculateAngleDiff(user_landmarks, user_image, self.last_user_pose, user_landmarks)

        if len(error_angles) > 0:
            self.keep_time_start_ = time.perf_counter()
            return state

        diff = time.perf_counter() - self.keep_time_start_
        if diff < self.KEEP_START:
            return state

        if diff < self.KEEP_OVER:
            recipcal = 'kepp {} sec'.format(int(self.KEEP_OVER - diff))
            cv2.putText(self.context_.evaluation_image_, recipcal, (40, 40), cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
            return state

        self.context_.current_task_.evaluation_landmark_ = (user_landmarks)
        self.context_.current_task_.image_ = user_image
        self.context_.current_task_.evaluation_angles = Util.translateLandmarks(user_landmarks, user_image.shape,
                                                                                user_image)

        return EvaluationState.COMPLETE


class NextAction:
    def __init__(self, context):
        self.context_ = context

        return

    def get_teacher_angles(self, idx):
        teacher_pose = self.context_.teacher_action_.m_teacher_pose[idx]
        image = self.context_.current_task_.teacher_image_
        teacher_angles = Util.translateLandmarks(teacher_pose['landmarks'], image.shape, image)

        return teacher_angles

    def score(self, user_landmarks, user_image):
        user_angles = self.context_.current_task_.evaluation_angles
        teacher_angels_0 = self.get_teacher_angles(0)
        teacher_angels_end = self.get_teacher_angles(self.context_.current_task_.teacher_pose_idx_)

        scores = []
        for idx in range(0, len(user_angles)):
            user_ability = user_angles[idx] - teacher_angels_0[idx]
            teacher_ability = teacher_angels_end[idx] - teacher_angels_0[idx]
            score = user_ability / teacher_ability * 100
            scores.append(score)

        self.context_.current_task_.scores_ = self.score()

        total_score = 0.0
        for score in scores:
            total_score += scores

        self.context_.current_task_.sychronize_score_ = total_score / len(user_angles)

        return scores

    def perform(self, user_landmarks, user_image):
        # 1.match teacher pose in evaluation range by min angle diff

        # 2. compare with evaluation position
        self.score()

        # 3.calculate score and recored result

        # 4.dispatch train task

        # 5.create report
        state = EvaluationState.INIT
        if self.context_.task_idx_ < len(self.context_.tasks_):
            self.context_.task_idx_ += 1
            state = EvaluationState.INIT
        else:
            state = EvaluationState.CREATE_REPORT

        return state


class CreateReport:
    def __init(self, context):
        self.context_ = context

        return

    def get_picture_file(self, landmarks, image, task):
        Util.translateLandmarks(landmarks, image.shape, image)

        height , width, _ = image.shape
        scale_y = float(512) / height
        scale_x = float(512) / width
        scale = scale_x
        if scale < scale_y :
            scale = scale_y
        image = cv2.resize(image, (width * scale, height * scale))

        file_name = '{}/{}.jpg'.format(g_config.get_report_path(), time.perf_counter())
        cv2.imwrite(file_name, image)

        return file_name

    def add_evaluation_result(self):
        paragraphs = []
        head1 = Paragraph("评估结果")
        paragraphs.append(head1)

        idx = 0
        for task in self.context_.tasks_ :
            # 1.craete a paragraph
            idx += 1
            title = Paragraph('{}. {}'.format(idx, task.j_config['action_name']))
            paragraphs.append(title)

            # 2.draw angle and picture for teacher and user
            teacher_pic = self.get_picture_file(task.teacher_landmarks_, task.teacher_image_)
            user_pic = self.get_picture_file(task.user_landmarks_, task.user_image_)

            # 3.add picture into this paragraph
            paragraphs.append(Image(teacher_pic))
            paragraphs.append(Image(user_pic))

            # 4.add describe
            paragraphs.append(Paragraph('total score:{}'.format(task.sychronize_scroe_)))
            paragraphs.append(Paragraph('item score:{}'.format(task.socres_)))

        return paragraphs

    def dispatch_train_task(self):
        head1 = Paragraph('根据评估结果的下期训练任务与目标')
        paragraphs = []
        paragraphs.append(head1)

        return paragraphs

    def create_graph(self, action_name, part):
        # 1. get all record
        records = g_config.get_evaluation_records(action_name)

        # 2. create polot for intesting angles
        datas = []
        for record in records :
            idx = g_config.get_idx_by_part(part)
            user_angle = record['user_angles'][idx]
            teacher_angle = record['teacher_angles'][idx]
            evaluate_date = datetime(record['datetime'])

            row = [user_angle, teacher_angle, evaluate_date]
            datas.append(row)

        # 3. craate pic
        cols = ['date', 'user', 'teacher']
        data = pd.DataFrame(datas, cols)
        fig = sns.lineplot(x="date", y="user", markers="o", data=data)
        scatter = fig.get_figure()

        file_name = '{}/{}_{}.jpg'.format(g_config.get_report_path(), action_name, part)
        scatter.savefig(file_name, dpi = 400)

        return file_name

    def statistical_analysis(self):
        paragraphs = []
        head1 = Paragraph(''.format('统计分析'))
        paragraphs.append(head1)

        for task in self.context_.tasks_ :
            parts = task.j_config['need_parts']
            for part in parts :
                file = self.create_graph(task.j_config['need_parts'], part)

                # add into doc
                paragraphs.append(Image(file))

                # add describe
                paragraphs.append(Paragraph('恢复速度较慢，主要原因是为保质保量完成每日训练！！！'))

        return paragraphs

    def save(self, paragraphs):
        action_name = self.context_.current_task_.j_config_['action_name']
        evaluation_time = datetime.datetime()

        file_name = '{}/{}_{}{}{}.pdf'.format(
            g_config.get_report_path(),
            action_name,
            evaluation_time.year, evaluation_time.month, evaluation_time.day)

        doc = SimpleDocTemplate(file_name)

        doc.build(paragraphs)

        return

    def perform(self, user_landmarks, user_image):
        paragraphs = self.add_evaluation_result()

        paragraphs += self.dispatch_train_task()

        paragraphs += self.statistical_analysis()

        self.save(paragraphs)

        return
