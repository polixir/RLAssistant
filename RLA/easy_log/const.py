LOG = 'log'
CODE = 'code'
CHECKPOINT = 'checkpoint'
ARCHIVE_TESTER = 'archive_tester'
HYPARAMETER = 'hyperparameter'
OTHER_RESULTS = 'results'
TMP_DATA = 'tmp_data'
ARCHIVED_TABLE = 'arc'
default_log_types = [LOG, CODE, CHECKPOINT, ARCHIVE_TESTER, OTHER_RESULTS, TMP_DATA, HYPARAMETER]
HYPARAM_FILE_NAME = 'parameter'

class LoadTesterMode:
    FORK_TO_NEW = 'fork'


# option: 'stdout', 'log', 'tensorboard', 'csv'
class LogDataType:
    TB = 'tensorboard'
    CSV = 'csv'
    TXT = 'log'
    STDOUT = 'stdout'
