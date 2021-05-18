
class TaskQueue :
    def __init__(self):
        self.tasks_ = {}

        return

    def add_task(self, task):
        try:
            self.tasks_[task.user_id] = task
        except Exception as e:
            print ('task_queue add_task except:{}'.format(e))

        return None

    def delete_task(self, user_id):
        try:
            self.tasks_.pop(user_id)
        except Exception as e :
            print ('task_queue delete_task except:{}'.format(e))

        return

    def get_task_by_userid(self, userid):
        try:
            task = self.tasks_[userid]
        except Exception as e :
            print ('task_queue get_taskby_userid except:{}'.format(e))

        return task


g_task_queue = TaskQueue()