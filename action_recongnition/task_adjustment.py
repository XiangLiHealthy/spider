from ConfigManager import  g_config

class TaskAdjustment :
    def __init__(self):

        return

    def get_last_tasks(self, name):
        config = g_config.get_task_config()
        actions = []
        for action in config['action_name'] :
            if name == action['action_name'] :
                actions.append(action)

        return actions

    def get_next_actions(self, name):
        task_config = g_config.get_task_config()
        for action in task_config['adjust_task_rule']['actions'] :
            if action['name'] == name:
                return action

        return None

    def get_evaluation_result(self, name):
        evaluation_result = g_config.get_evaluation_records(None)
        for evaluation in evaluation_result:
           if name == (evaluation['name']) :
               return evaluation

        return None

    def create_one_task(self, rule, evaluation):
        action = {}
        action['action_name'] = rule['action_name']
        action['frequency'] = rule['frequency']
        action['count'] = rule['count']
        action['keep_day'] = rule['keep_day']
        action['focus_parts'] = rule['focus_parts']
        action['last_time'] = ''

        return action

    def create_task(self):
        # get evaluation result
        evaluation_result = g_config.get_evaluation_records(None)
        last_tasks = []
        for evaluation in evaluation_result :
            last_tasks += self.get_last_tasks(evaluation['name'])

        # get all next actions
        next_actions = []
        for last_task in last_tasks :
            next_actions += self.get_next_actions(last_task['action_name'])

        if len(next_actions) == 0 :
            for evaluation in evaluation_result :
                next_actions += evaluation['next_acitons']

        # create task
        actions = []
        for name in next_actions :
            rule = self.get_next_actions(name)
            if None == rule :
                continue

            action = self.create_one_task(rule)
            action = self.adjust_angle(action, rule)
            if None == action :
                continue

            actions.append(action)

        return actions

    def adjust_angle(self, action, rule):
        evaluation_result = self.get_evaluation_result(action['name'])
        if None == evaluation_result :
            return None

        angle_ranges = []
        for part in evaluation_result['angle_range'] :
            angle_range = part

            if angle_range['start_angle'] <= angle_range['end_angle'] :
                angle_range['end_angle'] += rule['unit']
            else :
                angle_range['end_angle'] -= rule['unit']

            if angle_range['end_angle'] > 180 :
                angle_range['end_angle'] = 180
            elif angle_range['end_angle'] < 0 :
                angle_range['end_angle'] = 0

            angle_ranges.append(angle_range)

        action['angles_range'] = angle_ranges

        return action

    def perform(self):
        # create task
        tasks = self.create_task()

        #  adjust part angle
        self.adjust_angle(tasks)

        # save config
        g_config.save_task(tasks)

        return


g_adjustment = TaskAdjustment()