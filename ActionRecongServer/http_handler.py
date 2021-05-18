import time

from sanic.response import text
from sanic.response import json
from task_train import TaskTrain
from config_manager import g_config
from task_queue import g_task_queue
from command_handler import *
from uri_def import *


class HttpHandler:
    def __init__(self):

        return

    def perform(self, request):

        return text('no HttpHandler implement')


class SetActionHandlerImp(HttpHandler) :
    def __init__(self):

        return

    def perform(self, request):
        j_response = {}
        j_request = request.json

        try:
            while True :
                # 2.verify userid
                # 3. create recong task
                task = TaskTrain()
                task.action_name = j_request['action_name']
                task.user_id = j_request['user_id']
                task.solution = j_request['solution']
                task.count = j_request['task_count']
                # 4.set action name and load teacher model
                task.config = g_config.get_action_by_name(task.action_name)
                if None == task.config :
                    j_response['result'] = RESULT_FAILD
                    j_response['desc'] = 'get action:{} failed'.format(task.action_name)
                    break

                # 5. add task into queue
                g_task_queue.add_task(task)
                j_response['result'] = RESULTl_OK
                j_response['desc'] = 'load teacher action ok'
                break
        except Exception as e :
            print ('set action except:{}'.format(e))

        return json((j_response))


class UploadLandmarksHandler(HttpHandler) :
    def __init__(self):
        self.command_handlers_ = {
            COMMAND_TRAIN, TrainCommandImp()
        }

        return

    def perform(self, request):
        j_request = request.json
        j_response = {}

        try:
            while True:
                # get task from queue by userid
                task = g_task_queue.get_task_by_userid(j_request['user_id'])
                if None == task :
                    j_response['result'] = RESULT_FAILD
                    j_response['desc'] = 'get task from queue faild, user_id:{}'.format(j_request['user_id'])
                    break

                # update task time
                task.last_time = time.perf_counter()

                # case training/evaluation/free
                solution = task.solution
                landmarks = j_request['landmarks']
                data = self.command_handlers_[solution].perform(task, landmarks)
                j_response['data'] = data
                j_response['result'] = RESULTl_OK
                j_response['desc'] = ''

                break
        except Exception as e :
            print ('upload landmarks except :{}'.format(e))

        return json(j_response)


class FinishHandlerImp(HttpHandler) :
    def __init__(self):

        return

    def perform(self, request):
        j_response = {}

        try:
            # delete task
            j_request = request.json
            user_id = j_request['user_id']
            g_task_queue.delete_task(user_id)

            j_response['result'] = RESULTl_OK
            j_response['desc'] = 'ok'
        except Exception as e :
            print ('finish handler except:{}'.format(e))

        return json(j_response)
