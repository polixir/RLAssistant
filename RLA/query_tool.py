# Created by xionghuichen at 2022/8/10
# Email: chenxh@lamda.nju.edu.cn

import json
import glob
import os.path as osp
import os
import dill
import re
import copy
import json

from RLA.easy_log.const import * 
from RLA.easy_log.tester import Tester
from RLA.utils.utils import set_or_append, set_or_keep

from RLA.const import *
from RLA.utils.utils import get_dir_seperator, get_sys_type


class BasicQueryResult(object):
    def __init__(self, dirname):
        self.dirname = dirname

class ArchiveQueryResult(BasicQueryResult):
    def __init__(self, exp_manager, dirname):
        super(ArchiveQueryResult, self).__init__(dirname)
        assert isinstance(exp_manager, Tester)
        self.exp_manager = exp_manager


class LogQueryResult(BasicQueryResult):
    def __init__(self, dirname):
        super(LogQueryResult, self).__init__(dirname)

class HyperParamResult(BasicQueryResult):
    def __init__(self, dirname, hyper_param):
        super(HyperParamResult, self).__init__(dirname)
        self.hyper_param = hyper_param


class CkpResult(BasicQueryResult):
    def __init__(self, dirname, all_ckps):
        super(CkpResult, self).__init__(dirname)
        self.all_ckps = all_ckps


class OtherQueryResult(BasicQueryResult):
    def __init__(self, dirname, ctime, location):
        super(OtherQueryResult, self).__init__(dirname)
        self.ctime = ctime
        self.location = location

def extract_valid_index(regex):
    sys_type = get_sys_type()
    if sys_type == PLATFORM_TYPE.WIN:
        regex_pattern = r'\d{4}\\\d{2}\\\d{2}\\\d{2}-\d{2}-\d{2}-\d{6}'
    else:
        regex_pattern = r'\d{4}\d{2}/\d{2}/\d{2}-\d{2}-\d{2}-\d{6}'
    if re.search(regex_pattern, regex):
        target_reg = re.search(regex_pattern, regex).group(0)
    else:
        target_reg = None
    return target_reg


def single_experiment_query(data_root, task_table_name, log_date, data_type):

    """Query a single experiment data based on the given parameters.
    
    :param data_root: The root directory of the data.
    :param task_table_name: The name of the task table.
    :param log_date: The whole date of the log, e.g., 2023/07/30/13-32-43-819243
    :param data_type: Data type, including LOG, ARCHIVE_TESTER, OTHER_RESULTS, HYPARAMETER, and CHECKPOINT.
    :return: Returns the query result.
    """
    return experiment_data_query(data_root, task_table_name, log_date + '*', data_type, single_res_filter=True)

def experiment_data_query(data_root, task_table_name, reg, data_type, single_res_filter=False):
    """
    A function for querying experimental data based on data type.

    :param data_root: The root directory of the data.
    :param task_table_name: The name of the task table.
    :param reg: Regular expression.
    :param data_type: Data type, including LOG, ARCHIVE_TESTER, OTHER_RESULTS, HYPARAMETER, TMP_DATA, and CHECKPOINT.
    :param single_res_filter: Whether to filter the query results. If True, only one query result is returned, otherwise all query results are returned.
    :raises NotImplementedError: When the data type is not one of the above five types, a NotImplementedError exception is thrown.
    :return: Returns the query result.
    """
    
    if data_type == LOG:
        query_res = _log_data_query(data_root, task_table_name, reg)
    elif data_type == ARCHIVE_TESTER:
        query_res =  _archive_tester_query(data_root, task_table_name, reg)
    elif data_type == OTHER_RESULTS or data_type == TMP_DATA:
        query_res =  _results_data_query(data_root, task_table_name, reg, data_type)
    elif data_type == HYPARAMETER:
        query_res =  _results_hyparam_query(data_root, task_table_name, reg)
    elif data_type == CHECKPOINT:
        query_res =  _results_ckp_query(data_root, task_table_name, reg)
    else:
        raise NotImplementedError("Unsupported data type")
    if single_res_filter: 
        assert len(query_res.keys()) == 1, f"Error: More than one / none of result found, num: {len(query_res.keys())}"
        query_res = list(query_res.values())[0]
    return query_res
        

def _results_ckp_query(data_root, task_table_name, reg):
    experiment_data_dict = {}
    root_dir_regex = osp.join(data_root, CHECKPOINT, task_table_name, reg)
    for root_dir in glob.glob(root_dir_regex):
        if os.path.exists(root_dir):
            if osp.isdir(root_dir):
                for file_list in os.walk(root_dir):
                    for file in file_list[2]:
                        location = osp.join(file_list[0], file)
                        dirname = osp.dirname(location)
                        all_ckps = os.listdir(dirname)
                        if len(all_ckps) == 0:
                            continue
                        key = extract_valid_index(location)
                        experiment_data_dict[key] = CkpResult(dirname=dirname, all_ckps=all_ckps)
    return experiment_data_dict


def _results_hyparam_query(data_root, task_table_name, reg):
    experiment_data_dict = {}
    root_dir_regex = osp.join(data_root, HYPARAMETER, task_table_name, reg)
    for root_dir in glob.glob(root_dir_regex, recursive=True):
        if os.path.exists(root_dir):
            if osp.isdir(root_dir):
                for file_list in os.walk(root_dir):
                    for file in file_list[2]:
                        location = osp.join(file_list[0], file)
                        dirname = osp.dirname(location)
                        if os.path.exists(osp.join(dirname, HYPARAM_FILE_NAME + '.json')):
                            with open(osp.join(dirname, HYPARAM_FILE_NAME + '.json')) as f:
                                hyper_param = json.load(f)
                        elif os.path.exists(osp.join(dirname, HYPARAM_FILE_NAME + '.yaml')):
                            try:
                                from omegaconf import OmegaConf
                                with open(osp.join(dirname, HYPARAM_FILE_NAME + '.yaml')) as f:
                                    hyper_param = OmegaConf.load(f.name)
                            except Exception as e:
                                print("load omegaconf failed", e)
                        else:
                            continue
                        key = extract_valid_index(location)
                        experiment_data_dict[key] = HyperParamResult(dirname=dirname, hyper_param=hyper_param)
    return experiment_data_dict


def _results_data_query(data_root, task_table_name, reg, data_type):
    experiment_data_dict = {}
    def _other_res_append(inpt_key, inpt_dirname, inpt_location, inpt_ctime):
        if inpt_key not in experiment_data_dict.keys():
            experiment_data_dict[inpt_key] = OtherQueryResult(dirname=inpt_dirname,
                                                              location=[inpt_location], ctime=[inpt_ctime])
        else:
            experiment_data_dict[inpt_key].location.append(inpt_location)
            experiment_data_dict[inpt_key].ctime.append(inpt_ctime)

    root_dir_regex = osp.join(data_root, data_type, task_table_name, reg)
    for root_dir in glob.glob(root_dir_regex):
        if os.path.exists(root_dir):
            key = extract_valid_index(root_dir)
            if osp.isdir(root_dir) and key is not None:
                dirname = root_dir
                for file_list in os.walk(root_dir):
                    for file in file_list[2]:
                        location = osp.join(file_list[0], file)
                        ctime = os.path.getmtime(location)
                        key = extract_valid_index(location)
                        _other_res_append(key, dirname, location, ctime)
            else:
                location = root_dir
                key = extract_valid_index(location)
                ctime = os.path.getmtime(location)
                dirname = osp.dirname(location)
                _other_res_append(key, dirname, location, ctime)
    return experiment_data_dict

def _archive_tester_query(data_root, task_table_name, reg):
    experiment_data_dict = {}
    root_dir_regex = osp.join(data_root, ARCHIVE_TESTER, task_table_name, reg)
    for root_dir in glob.glob(root_dir_regex):
        if os.path.exists(root_dir):
            if osp.isdir(root_dir):
                for file_list in os.walk(root_dir):
                    for file in file_list[2]:
                        location = osp.join(file_list[0], file)
                        exp_manager = dill.load(open(location, 'rb'))
                        dirname = location.split('.pkl')[0]
                        key = extract_valid_index(location)
                        experiment_data_dict[key] = ArchiveQueryResult(dirname=dirname, exp_manager=exp_manager)
            else:
                location = root_dir
                key = extract_valid_index(location)
                exp_manager = dill.load(open(location, 'rb'))
                dirname = location.split('.pkl')[0]
                experiment_data_dict[key] = ArchiveQueryResult(dirname=dirname, exp_manager=exp_manager)
    return experiment_data_dict


def _log_data_query(data_root, task_table_name, reg):
    experiment_data_dict = {}
    root_dir_regex = osp.join(data_root, LOG, task_table_name, reg)
    for root_dir in glob.glob(root_dir_regex):
        if os.path.exists(root_dir):
            if osp.isdir(root_dir):
                for file_list in os.walk(root_dir):
                    for file in file_list[2]:
                        if 'progress.csv' in file:
                            location = osp.join(file_list[0], file)
                            key = extract_valid_index(location)
                            dirname = osp.dirname(location)
                            experiment_data_dict[key] = LogQueryResult(dirname=dirname)
                            break
            else:
                location = root_dir
                dirname = osp.dirname(location)
                experiment_data_dict[key] = LogQueryResult(dirname=dirname)
    return experiment_data_dict

