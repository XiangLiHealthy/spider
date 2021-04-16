import cv2
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
from task_adjustment import g_adjustment
from datetime import date
from evaluation_state import EvaluationState

class Teaching:
    def __init__(self, context):
        self.context_ = context
        self.video_idx_ = 0
        self.play_times_ = 0
        self.video_path_ = ''

        return

    def setImage(self):
        try:
            if self.video_path_ != self.context_.current_task_.j_config_['video_path']:
                self.video_path_ = self.context_.current_task_.j_config_['video_path']
                self.video_idx_ = 0
                self.play_times_ = 0
                self.context_.video_manager_.setVideo(self.video_path_)

            self.context_.evaluation_image_ = self.context_.video_manager_.getFrameByIdx(self.video_idx_)
            self.video_idx_ += 1
        except Exception as e :
            print ('setImage except: {}'.format(e))

        return

    def showTips(self, user_imnage):
        try:
            # where can L get tips content
            tips = self.context_.current_task_.j_config_['tips']

            y = 40
            for tip in tips :
                cv2.putText(self.context_.evaluation_image_, tip, (40, y), cv2.FONT_HERSHEY_PLAIN, 2.0,
                            (0, 0, 255), 2)
                y += 20

        except Exception as e :
            print ('showTips except :{}'.format(e))

        return

    def perform(self, user_landmarks, user_image):
        try:
            # 1.play video
            self.setImage()

            # 2.tips text
            self.showTips(user_image)

            # increament times if play ok
            frame_count = self.context_.video_manager_.getFrameCount()
            if frame_count == self.video_idx_:
                self.play_times_ += 1
                self.video_idx_ = 0

            # return next state if times ok
            state = EvaluationState.TEACHING
            if self.context_.current_task_.j_config_['play_times'] <= self.play_times_:
                state = EvaluationState.PREPARE
        except Exception as e :
            print ('teaching perform except : {}'.format(e))

        return state


class Prepare:
    def __init__(self, context):
        self.teacher_image_ = None
        self.context_ = context  # context
        self.pose_idx_ = 0

        return

    def setTeacherPose(self):
        try:
            # 1. get first pose landmarks and image
            pose = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]

            # 2.
            idx = pose['frame_num']
            self.context_.current_task_.teacher_image_ = self.context_.video_manager_.getFrameByIdx(idx)
            self.context_.evaluation_image_ = self.context_.current_task_.teacher_image_
            self.context_.current_task_.teacher_landmarks = pose['landmarks']
        except Exception as e :
            print ('setTeacherPose except : {}'.format(e))

        return

    def drawTeacherTips(self):
        try:
            tips = self.context_.teacher_action_.m_teacher_pose[self.pose_idx_]['tips']

            point = (40, 40)
            cv2.putText(self.context_.evaluation_image_, tips, point, cv2.FONT_HERSHEY_PLAIN, 2.0,
                        (0, 0, 255), 2)
        except Exception as e :
            print ('drawTeacherTips except :{}'.format(e))

        return

    def perform(self, user_landmarks, user_image):
        try:
            # 1.set teacher pose
            self.setTeacherPose()

            # 2. show teacher tips
            self.drawTeacherTips()

            # 3. recong user pose
            error_angles = Util.calculateAngleDiff(user_landmarks, user_image,
              self.context_.current_task_.teacher_landmarks, self.context_.evaluation_image_)

            # 4. error tips
            Util.pointErrorAngle(error_angles, user_landmarks, user_image)

            # 5. change state
            state = EvaluationState.PREPARE
            if 0 == len(error_angles):
                state = EvaluationState.EVALUATING
        except Exception as e :
            print('prepar except:{}'.format(e))

        return state


class Evaluating(Prepare):
    def __init__(self, context):
        super().__init__(context)

        return

    def initPoseIdx(self):
        try:
            # 1.get evaluation position
            position = self.context_.current_task_.j_config_['target_ability']

            # 2. get teacher pose num
            pose_num = len(self.context_.teacher_action_.m_teacher_pose)

            # 3. calculate pose idx
            self.pose_idx_ = int(pose_num * position)
            self.context_.current_task_.teacher_pose_idx_ = self.pose_idx_
        except Exception as e :
            print ('evaluating initPoseIdx except : {}'.format(e))

        return

    def perform(self, user_landmarks, user_image):
        try:
            # 1.init pose idx
            self.initPoseIdx()

            # 2.set teacher pose
            super().setTeacherPose()

            # 3. show teaacher tips
            super().drawTeacherTips()

            # 4. change state
        except Exception as e :
            print ('evaluating perform except:{}'.format(e))

        return EvaluationState.KEEP_POSE


class Keeping:
    def __init__(self, context):
        self.keep_time_start_ = 0
        self.last_landmarks = []

        self.KEEP_START = 1
        self.KEEP_OVER = 5
        self.landmarks_cache_ = []
        self.context_ = context

        return

    def get_last_sec_landmarks(self, current_landmarks):
        try:
            # if first landmarks is last sec,del and return
            item = {}
            current_time = time.perf_counter()
            item['time'] = current_time
            item['landmarks'] = current_landmarks
            self.landmarks_cache_.append(item)

            landmarks = self.landmarks_cache_[0]
            if current_time - landmarks['time'] > self.KEEP_START :
                del self.landmarks_cache_[0]
                return landmarks['landmarks']
        except Exception as e :
            print ('get_last_sec_landmarks except : {}'.format(e))

        return None

    def perform(self, user_landmarks, user_image):
        try:
            state = EvaluationState.KEEP_POSE
            last_sec_landmarks = self.get_last_sec_landmarks(user_landmarks)
            if None == last_sec_landmarks :
                return state

            error_angles = Util.calculateAngleDiff(user_landmarks, user_image, last_sec_landmarks, user_image)

            if len(error_angles) > 0:
                self.keep_time_start_ = time.perf_counter()
                return state

            diff = time.perf_counter() - self.keep_time_start_
            if diff < self.KEEP_OVER:
                recipcal = 'kepp {} sec'.format(int(self.KEEP_OVER - diff))
                cv2.putText(self.context_.evaluation_image_, recipcal, (40, 40), cv2.FONT_HERSHEY_PLAIN, 2.0,
                            (0, 0, 255), 2)
                return state

            self.context_.current_task_.evaluation_landmark_ = user_landmarks
            self.context_.current_task_.image_ = user_image
            self.context_.current_task_.evaluation_angles = Util.translateLandmarks(user_landmarks, user_image.shape,
                          user_image)
        except Exception as e :
            print ('keeping perform except :{}'.format(e))

        return EvaluationState.NEXT


class NextAction:
    def __init__(self, context):
        self.context_ = context

        return

    def get_teacher_angles(self, idx):
        try:
            teacher_pose = self.context_.teacher_action_.m_teacher_pose[idx]
            image = self.context_.current_task_.teacher_image_
            teacher_angles = Util.translateLandmarks(teacher_pose['landmarks'], image.shape, image)
        except Exception as e :
            print ('NextAction get_teacher_angles except:{}'.format(e))

        return teacher_angles

    def score(self):
        try:
            user_angles = self.context_.current_task_.evaluation_angles
            teacher_angels_0 = self.get_teacher_angles(0)
            teacher_angels_end = self.get_teacher_angles(self.context_.current_task_.teacher_pose_idx_)
            self.context_.current_task_.teacher_angle_0 = self.get_teacher_angles(0)

            scores = []
            for idx in range(0, len(user_angles)):
                user_ability = user_angles[idx] - teacher_angels_0[idx]
                teacher_ability = teacher_angels_end[idx] - teacher_angels_0[idx]
                score = user_ability / teacher_ability * 100
                scores.append(score)

            self.context_.current_task_.scores_ = scores

            total_score = 0.0
            for score in scores:
                total_score += scores

            self.context_.current_task_.sychronize_score_ = total_score / len(user_angles)
        except Exception as e :
            print ('score except:{}'.format(e))

        return scores

    def perform(self, user_landmarks, user_image):
        try:
            # 1.match teacher pose in evaluation range by min angle diff

            # 2. compare with evaluation position
            self.score()

            # 3.calculate score and recored result

            # 4.dispatch train task
            g_config.setEvaluationState(self.context_.current_task_.j_config_['action_name'], EvaluationState.COMPLETE)

            # 5.create report
            state = EvaluationState.INIT
            if self.context_.task_idx_ + 1 < len(self.context_.tasks_):
                self.context_.task_idx_ += 1
                state = EvaluationState.INIT
            else:
                state = EvaluationState.CREATE_REPORT
        except Exception as e :
            print ('NextAction perform except:{}'.format(e))

        return state


class CreateReport:
    def __init__(self, context):
        self.context_ = context

        return

    def get_picture_file(self, landmarks, image):
        try:
            Util.translateLandmarks(landmarks, image.shape, image)

            height , width, _ = image.shape
            scale_y = float(512) / height
            scale_x = float(512) / width
            scale = scale_x
            if scale > scale_y :
                scale = scale_y
            image = cv2.resize(image, (width * scale, height * scale))

            file_name = '{}/{}.jpg'.format(g_config.get_report_path(), time.perf_counter())
            cv2.imwrite(file_name, image)
        except Exception as e :
            print ('get_pic_file except:{}'.format(e))

        return file_name

    def add_evaluation_result(self):
        try:
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
        except Exception as e :
            print ('add_evaluation_result except:{}'.format(e))

        return paragraphs

    def save_evaluation_results(self):
        try:
            # get all tasks
            tasks_results = self.context_.tasks_

            for result in tasks_results :
                j_config = result.j_config_
                focus_parts = j_config['focus_part']
                angle_0 = self.context_.current_task_.teacher_angle_0
                angle_end = Util.translateLandmarks(self.context_.current_task_.teacher_landmarks, None, None)

                angles_range = []
                for part in focus_parts :
                    idx = g_config.get_idx_by_part(part)
                    range = {}
                    range['name'] = part
                    range['start_angle'] = angle_0[idx]
                    range['end_angle'] = angle_end[idx]
                    angles_range.append(range)

                result_item = {}
                result_item['angle_range'].append(angles_range)
                result_item['date_time'] = date.fromisoformat()
                result_item['adjust_flag'] = 'not_adjust'
                j_config['results'].append(result_item)

            # change evaluation into config
            g_config.save_evaluation_results(tasks_results)
        except Exception as e :
            print ('save_evaluation_results except :{}'.format(e))

        return

    def adjust_train_task(self):
        try:
            self.save_evaluation_results()
            tasks = g_adjustment.perform()

            head1 = Paragraph('根据评估结果的下期训练任务与目标')
            paragraphs = []
            paragraphs.append(head1)

            idx = 0
            for task in tasks :
                idx += 1
                text = '{}.{},count/day, {} day'.format(task['action_name'], task['count'], task['cycle'])
                paragraphs.append(text)
                for angle_range in task['angle_range'] :
                    range = '  {} : ({}, {})'.format(angle_range['name'], angle_range['min'], angle_range['max'])
                    paragraphs.append(range)
        except Exception as e :
            print ('adjust_trein_task except :{}'.format(e))

        return paragraphs

    def create_graph(self, action_name, part):
        try:
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
        except Exception as e :
            print ('create_graph except:{}'.format(e))

        return file_name

    def statistical_analysis(self):
        try:
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
        except Exception as e :
            print ('statistical_ananasis except:{}'.format(e))

        return paragraphs

    def save(self, paragraphs):
        try:
            action_name = self.context_.current_task_.j_config_['action_name']
            evaluation_time = datetime.datetime()

            file_name = '{}/{}_{}{}{}.pdf'.format(
                g_config.get_report_path(),
                action_name,
                evaluation_time.year, evaluation_time.month, evaluation_time.day)

            doc = SimpleDocTemplate(file_name)

            doc.build(paragraphs)
        except Exception as e :
            print ('CreateReport except:{}'.format(e))

        return

    def perform(self, user_landmarks, user_image):
        try:
            paragraphs = self.add_evaluation_result()

            paragraphs += self.adjust_train_task()

            paragraphs += self.statistical_analysis()

            self.save(paragraphs)
        except Exception as e :
            print ('CreateReport perform except:{}'.format(e))

        return EvaluationState.COMPLETE
