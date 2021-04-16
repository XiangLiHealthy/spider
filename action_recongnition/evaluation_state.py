from enum import Enum


class EvaluationState(Enum):
    INIT = 0
    TEACHING = -1
    PREPARE = 1
    EVALUATING = 2
    KEEP_POSE = 3
    COMPLETE = 4
    NEXT = 5
    CREATE_REPORT = 6