from RLA.easy_log import logger
from RLA.easy_log.tester import exp_manager, Tester
import copy
import argparse
from typing import Optional
from RLA.const import DEFAULT_X_NAME
from pprint import pprint
from RLA.easy_log.const import *
from RLA.query_tool import experiment_data_query, single_experiment_query

class ExperimentLoader(object):
    """
    We can use a combination of the functions: import_hyper_parameters, load_from_record_date and fork_tester_log_files
    to construct classical tasks.
    -  Start a new task: do nothing.
    -  load a pretrained model for another task (e.g., validation):
        0. config loaded_task_name and loaded_date to the task and timestamp of the target experiment to load respectively.
        1. init your exp_manager;
        2. call exp_loader.load_from_record_date to resume the neural networks and intermediate variables.
        3. start your process.
    - resume an experiment:
        0. config loaded_task_name and loaded_date to the task and timestamp of the target experiment to load respectively.
        1. init your exp_manager;
        2. call exp_loader.fork_log_files to copy all of the log data of the target experiment to the current experiment.
        3. call exp_loader.load_from_record_date to resume the neural networks and intermediate variables.
        4. start your process.
    - resume an experiment with other settings.
        0. config loaded_task_name and loaded_date to the task and timestamp of the target experiment to load respectively.
        1. call exp_loader.load_from_record_date
        2. call import_hyper_parameters to resume the hyper-parameters of the target experiment
            and use hp_to_keep to overwrite the hyper-parameters that you want to update for the new test.
        3. call exp_loader.load_from_record_date to resume the neural networks and intermediate variables.
        4. start your process.
    """
    def __init__(self):
        self.task_name = exp_manager.hyper_param.get('loaded_task_name', None)
        self.load_date = exp_manager.hyper_param.get('loaded_date', None)
        self.data_root = getattr(exp_manager, 'data_root', None)
        if self.data_root is None:
            self.data_root = getattr(exp_manager, 'root', None)
        pass

    def config(self, task_name, record_date, root):
        self.task_name = task_name
        self.load_date = record_date
        self.data_root = root

    @property
    def is_valid_config(self):
        if self.load_date is not None and self.task_name is not None and self.data_root is not None:
            return True
        else:
            logger.warn("meet invalid loader config when using it")
            logger.warn("load_date", self.load_date)
            logger.warn("task_name", self.task_name)
            logger.warn("root", self.data_root)
            return False
    
    def get_hyperparameters(self, hp_to_overwrite: Optional[list] = None):
        # find 
        pass

    def import_hyper_parameters(self, hp_to_overwrite: Optional[list] = None, sync_timestep=False):
        if self.is_valid_config:
            # loaded_tester = Tester.load_tester(self.load_date, self.task_name, self.data_root)
            target_hp = copy.deepcopy(exp_manager.hyper_param)
            try:
                query_res = single_experiment_query(self.data_root, self.task_name, self.load_date, HYPARAMETER)
                load_config = query_res.hyper_param
            except AssertionError as e:
                loaded_tester = Tester.load_tester(self.load_date, self.task_name, self.data_root)
                load_config = loaded_tester.hyper_param
            target_hp.update(load_config)
            if hp_to_overwrite is not None:
                for k in hp_to_overwrite:
                    if '.' in k:
                        sub_k = None
                        try:
                            sub_k_list = k.split('.')
                            sub_k = sub_k_list[0]
                            v = target_hp[sub_k]
                            origin_v = exp_manager.hyper_param[sub_k]
                            for sub_k in sub_k_list[1:-1]:
                                v = v[sub_k]
                                origin_v = origin_v[sub_k]
                            v[sub_k_list[-1]] = origin_v[sub_k_list[-1]]
                        except KeyError as e:
                            print(f"the current key to parsed is: {k}. Can not find a matching key for {sub_k}."
                                "\n Hint: do not include dot ('.') in your hyperparemeter name."
                                "\n The recorded hyper parameters are")
                    else:
                        target_hp[k] = exp_manager.hyper_param[k]
            args = argparse.Namespace(**target_hp)
            args.loaded_date = self.load_date
            args.loaded_task_name = self.task_name
            if sync_timestep:
                load_iter = loaded_tester.get_custom_data(DEFAULT_X_NAME)
                exp_manager.time_step_holder.set_time(load_iter)
            return args
        else:
            return argparse.Namespace(**exp_manager.hyper_param)

    def load_from_record_date(self, var_prefix: Optional[str] = None, variable_list: Optional[list]=None, verbose=True,
                              ckp_index: Optional[int]=None, checkpoint_name: Optional[str] = 'checkpoint'):
        """

        :param var_prefix: the prefix of namescope (for tf) to load. Set to '' to load all of the parameters.
        :param variable_list: the saved variables in the process of training, e.g., data buffer, decayed learning rate.
        :return:
        """
        if self.is_valid_config:
            loaded_tester = Tester.load_tester(self.load_date, self.task_name, self.data_root)
            if verbose:
                print("attrs of the loaded tester")
                pprint(loaded_tester.__dict__)
            # load checkpoint
            load_res = {}
            if var_prefix is not None:
                loaded_tester.new_saver(var_prefix=var_prefix, max_to_keep=1, verbose=verbose)
                _, load_res = loaded_tester.load_checkpoint(ckp_index, checkpoint_name=checkpoint_name)
            else:
                loaded_tester.new_saver(max_to_keep=1, verbose=verbose)
                _, load_res = loaded_tester.load_checkpoint(ckp_index, checkpoint_name=checkpoint_name)
            hist_variables = {}
            if variable_list is not None:
                for v in variable_list:
                    hist_variables[v] = loaded_tester.get_custom_data(v)
            load_iter = loaded_tester.get_custom_data(DEFAULT_X_NAME)
            return load_iter, load_res, hist_variables
        else:
            return 0, {}, {}

    def fork_log_files(self, hp_to_overwrite: Optional[list] = None, sync_timestep=False, sync_hyper_param=False):
        """
        Fork the log files of a loaded experiment to the current experiment, and update the hyperparameters and timestep if needed.
        :param hp_to_overwrite: List of hyperparameters to overwrite with the current experiment's values.
        :param sync_timestep: If True, synchronize the timestep of the current experiment with the loaded experiment.
        """
        if self.is_valid_config:
            global exp_manager
            assert isinstance(exp_manager, Tester)
            loaded_tester = Tester.load_tester(self.load_date, self.task_name, self.data_root)
            # copy log file
            exp_manager.log_file_copy(loaded_tester)
            if sync_hyper_param:
                # copy attribute
                new_hp = copy.deepcopy(exp_manager.hyper_param)
                new_hp.update(loaded_tester.hyper_param)
                if hp_to_overwrite is not None:
                    # if '.' in k:
                    #     sub_k = None
                    #     try:
                    #         sub_k_list = k.split('.')
                    #         sub_k = sub_k_list[0]
                    #         v = self.hyper_param[sub_k]
                    #         for sub_k in sub_k_list[1:]:
                    #             v = v[sub_k]
                    #         self.hyper_param_record.append(str(k) + '=' + str(v).replace('[', '{').replace(']', '}').replace('/', '_'))
                    #     except KeyError as e:
                    #         print(f"the current key to parsed is: {k}. Can not find a matching key for {sub_k}."
                    #             "\n Hint: do not include dot ('.') in your hyperparemeter name."
                    #             "\n The recorded hyper parameters are")
                    #         self.print_args()
                    for v in hp_to_overwrite:
                        target_hp[v] = exp_manager.hyper_param[v]
                if sync_timestep:
                    load_iter = loaded_tester.get_custom_data(DEFAULT_X_NAME)
                    exp_manager.time_step_holder.set_time(load_iter)


exp_loader = experimental_loader = ExperimentLoader()

def fork_log_file_fn(task_name, record_date, root, hp_to_overwrite: Optional[list] = None, sync_timestep=False, sync_hyper_param=False):
    tmp_exp_loader = ExperimentLoader()
    tmp_exp_loader.config(task_name, record_date, root)
    tmp_exp_loader.fork_log_files(hp_to_overwrite=hp_to_overwrite, sync_timestep=sync_timestep, sync_hyper_param=sync_hyper_param)

def update_hyper_parameters_fn(task_name, record_date, root, hp_to_overwrite: Optional[list] = None, sync_timestep=False):
    tmp_exp_loader = ExperimentLoader()
    tmp_exp_loader.config(task_name, record_date, root)
    tmp_exp_loader.import_hyper_parameters(hp_to_overwrite=hp_to_overwrite, sync_timestep=sync_timestep)
