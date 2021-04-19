from ConfigManager import  g_config

class TaskAdjustment :
    def __init__(self):

        return

    def get_last_evaluations(self, evaluation):
        size = len(evaluation['results'])
        if size == 0 :
            return None

        result = evaluation['results'][size - 1]
        if result['adjust_flag'] == "adjusted" :
            return None

        evaluation['results'][size - 1]['adjust_flag'] = 'adjusted'

        return result

    def get_rule(self, name):
        task_config = g_config.get_task_config()
        for rule in task_config['adjust_task_rule']['actions'] :
            if rule['action_name'] == name:
                return rule

        return None

    def get_evaluation_result(self, name):
        evaluation_result = g_config.get_evaluation_records(None)
        for evaluation in evaluation_result:
           if name == (evaluation['action_name']) :
               return evaluation

        return None

    def create_one_task(self, rule):
        action = {}
        action['action_name'] = rule['action_name']
        action['frequency'] = rule['frequency']
        action['count'] = rule['count']
        action['keep_day'] = rule['keep_day']
        action['focus_parts'] = rule['focus_parts']
        action['last_time'] = ''

        return action

    def create_task(self):
        try:
            # get evaluation result
            actions = []
            evaluation_result = g_config.get_evaluation_records(None)
            last_evaluations = []
            for evaluation in evaluation_result :
                tmp = self.get_last_evaluations(evaluation)
                if None == tmp :
                    continue

                next_actions = evaluation['adjust_actions']
                for name in next_actions:
                    rule = self.get_rule(name)
                    if None == rule:
                        continue

                    action = self.create_one_task(rule)
                    action = self.adjust_angle(action, rule, tmp)
                    if None == action:
                        continue

                    actions.append(action)
        except Exception as e :
            print ('create task except :{}'.format(e))

        return actions

    def adjust_angle(self, action, rule, evaluation):
        try:
            angle_ranges = []
            for part in evaluation['angle_range'] :
                angle_range = part

                if angle_range['start_angle'] <= angle_range['end_angle'] :
                    angle_range['end_angle'] += rule['angle_change_unit']
                else :
                    angle_range['end_angle'] -= rule['angle_change_unit']

                if angle_range['end_angle'] > 180 :
                    angle_range['end_angle'] = 180
                elif angle_range['end_angle'] < 0 :
                    angle_range['end_angle'] = 0

                angle_ranges.append(angle_range)

            action['angles_range'] = angle_ranges
        except Exception as e :
            print (e)

        return action

    def perform(self):
        # create task
        tasks = self.create_task()

        #  adjust part angle
        #self.adjust_angle(tasks)

        # save config
        g_config.save_task(tasks)

        return


g_adjustment = TaskAdjustment()