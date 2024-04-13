# Created by xionghuichen at 2022/12/6
# Email: chenxh@lamda.nju.edu.cn
"""
A script to migrate some important experiments in one task table to the target task table.


"""
from rla_script_config import *
from RLA.easy_log.log_tools import MigrateLogTool
import argparse


def argsparser():
    parser = argparse.ArgumentParser("Migrate Log")
    # reduce setting
    parser.add_argument('--proj_root', type=str, default=DATA_ROOT)
    parser.add_argument('--target_proj_root', type=str, default=DATA_ROOT)
    parser.add_argument('--task_table', type=str)
    parser.add_argument('--target_task_table', type=str)
    parser.add_argument('--regex', type=str)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = argsparser()
    dlt = MigrateLogTool(proj_root=args.proj_root, target_proj_root=args.target_proj_root, task_table_name=args.task_table,
                         regex=args.regex,
                         target_task_table_name=args.target_task_table)
    dlt.migrate_log()

