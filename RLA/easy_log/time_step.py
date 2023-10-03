from RLA.easy_log import logger
import time

class TimeStepHolder(object):

    def __init__(self, time=0, epoch=0, tf_log=False):
        self.__timesteps = time
        self.__outer_epoch = epoch
        self.tf_log = tf_log

    def config(self, time=0, tf_log=False):
        self.__timesteps = time
        self.tf_log = tf_log

    def set_time(self, time):
        self.__timesteps = time
        self.__update_tf_times()

    def inc_time(self):
        self.__timesteps += 1
        self.__update_tf_times()

    def get_time(self):
        return self.__timesteps

    def add_time(self, add):
        self.__timesteps += add
        self.__update_tf_times()

    def __update_tf_times(self):
        if self.tf_log:
            found = False
            for fmt in logger.Logger.CURRENT.output_formats:
                if isinstance(fmt, logger.TensorBoardOutputFormat):
                    fmt.step = self.__timesteps
                    found = True
            assert found

time_step_holder = TimeStepHolder(0, 0, True)