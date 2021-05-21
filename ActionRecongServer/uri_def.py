from enum import Enum

URI_SET_ACTION = '/train/set_action'
URI_UPLOAD_LANDMARKS = '/train/upload_landmarks'
URI_FINISH = '/train/finish'

COMMAND_TRAIN = 'train'
COMMAND_EVALUATION = 'evaluation'

RESULT_FAILD = 'failed'
RESULTl_OK = 'ok'

LISTEN_PORT = 8888

class MOVE_DIRECTION(Enum):
    UP = 0,
    DOWN = 1,
    REVERT = 2,
    UNKNOWN = 3