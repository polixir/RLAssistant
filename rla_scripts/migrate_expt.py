# Created by xionghuichen at 2022/12/6
# Email: chenxh@lamda.nju.edu.cn
"""
A script to move some important experiments to another task_table


"""
from rla_script_config import *
from RLA.easy_log.log_tools import MoveLogTool
import argparse

def argsparser():
    parser = argparse.ArgumentParser("Archive Log")
    # reduce setting
    parser.add_argument('--task_table', type=str)
    parser.add_argument('--target_task_table', type=str)
    parser.add_argument('--regex', type=str)

    args = parser.parse_args()
    return args

if __name__=='__main__':
    args = argsparser()
    dlt = MoveLogTool(proj_root=DATA_ROOT, task_table_name=args.task_table, regex=args.regex,
                      target_task_table_name=args.target_task_table)
    dlt.archive_log()