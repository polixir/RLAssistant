# Created by xionghuichen at 2023/7/3
# Email: chenxh@lamda.nju.edu.cn
import os.path as osp
import os
import json
from RLA import logger
from RLA.const import DEFAULT_X_NAME
from RLA.query_tool import experiment_data_query, extract_valid_index
from RLA.easy_plot import plot_util
from RLA.easy_log.const import LOG, ARCHIVE_TESTER, OTHER_RESULTS, HYPARAM
from RLA.easy_plot.result_cls import Result

def results_loader(data_root, task_table_name, regs, hp_filter_dict, data_loader_func, verbose):
    results = []
    reg_group = {}
    for reg in regs:
        reg_group[reg] = []
        print("searching", reg)
        tester_dict = experiment_data_query(data_root, task_table_name, reg, ARCHIVE_TESTER)
        log_dict = experiment_data_query(data_root, task_table_name, reg, LOG)
        counter = 0
        for k, v in log_dict.items():
            result = data_loader_func(v.dirname)
            if result is None: continue
            assert isinstance(result, Result)
            # add hyper parameters
            if os.path.exists(osp.join(v.dirname, HYPARAM + '.json')):
                with open(osp.join(v.dirname, HYPARAM + '.json')) as f:
                    result.hyper_param = json.load(f)
            else:
                result.hyper_param = tester_dict[k].exp_manager.hyper_param
            if hp_filter_dict is not None:
                skip = False
                for k_hpf, v_hpf in hp_filter_dict.items():
                    v_hpf = [str(v) for v in v_hpf]
                    if k_hpf not in result.hyper_param.keys():
                        if verbose:
                            print(f"[WARN] the key {k_hpf} in hp_filter_dict can not be found in the experiment log", v.dirname)
                    else:
                        target_v = result.hyper_param[k_hpf]
                        if str(target_v) not in v_hpf:
                            if verbose:
                                print(f"skip the experiment log {v.dirname} which {k_hpf} is {target_v} not in {v_hpf}")
                            skip = True
                            break
                if skip:
                    continue
            counter += 1
            # if verbose:
            #     print("find log", v.dirname, "\n [parsed key]", key_to_legend_fn(result.hyper_param, split_keys, '', False))
            results.append(result)
            reg_group[reg].append(result)
        print("find log number", counter)
    return results, reg_group