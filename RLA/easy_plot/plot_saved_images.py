# Created by xionghuichen at 2023/7/2
# Email: chenxh@lamda.nju.edu.cn
import os
from typing import Dict, List, Tuple, Type, Union, Optional, Callable
from RLA.easy_plot.result_cls import ImgResult
from RLA.easy_plot.utils import results_loader
from RLA.easy_log.const import LOG, ARCHIVE_TESTER, OTHER_RESULTS, HYPARAM
from RLA.query_tool import OtherQueryResult
from RLA.easy_plot.result_cls import ImgResult
import numpy as np
import pathspec
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib

def meta_image_data_loader_func(query_res, selected_images, max_keep_num):
    assert isinstance(query_res, OtherQueryResult)
    dirname = query_res.dirname
    data_dict = {}
    for img in selected_images:
        ret_lines = [os.path.join(os.path.abspath(dirname), img)]
        spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, ret_lines)
        abs_loc = [os.path.abspath(loc) for loc in query_res.location]
        match_paths = np.array(list(set(spec.match_files(abs_loc))))
        # print("rule", ret_lines, "match_paths", match_paths, "query_res.location", query_res.location)
        if len(match_paths) > max_keep_num:
            match_ctimes = []
            for loc in match_paths:
                match_ctimes.append(os.path.getctime(loc))
            idx = np.argsort(match_ctimes)
            data_dict[img] = match_paths[idx[-1 * max_keep_num:]]
        else:
            data_dict[img] = match_paths
    return ImgResult(img_path_dict=data_dict, dirname=dirname)

def plot_saved_images(data_root:str, task_table_name:str, regs:list, img_names:list, hp_filter_dict: Optional[dict] = None,
                      verbose:bool = False, max_keep_num:int = 1, summarize_res=True):
    """
    :param data_root: Root directory for the data.
    :type data_root: str
    :param task_table_name: Task table name.
    :type task_table_name: str
    :param regs: List of regular expressions used for matching files/directories.
    :type regs: list
    :param hp_filter_dict: a dict to filter your log.
    e.g., hp_filter_dict= {'learning_rate': [0.001, 0.01, 0.1]} will select the logs where the learning rate is 0.001, 0.01, or 0.1.
    :param verbose: If True, prints detailed log information during the process.
    :type verbose: bool, default to True
    :param img_names: a list of image_name pattern for plotting.
    :type verbose: list, default to 1
    :param max_keep_num: for each image_name pattern in img_names, when multiple images satisfy the patterns, we will keep the latest saved images.
    The max number to keep is controlled by max_keep_num.
    :type verbose: int, default to 1
    """

    image_data_loader_func = lambda dirname: meta_image_data_loader_func(dirname, img_names, max_keep_num)
    results, reg_group = results_loader(data_root, task_table_name, regs, hp_filter_dict, image_data_loader_func,
                                        verbose, data_type=OTHER_RESULTS)
    if summarize_res:
        for k, v in reg_group.items():
            print(f"for regex {k}, we have the following results:")
            for res in v:
                print("find log", res.dirname)

    # TODO: split and group by keys
    for reg in regs:
        print(f"---print reg {reg} ----")
        for res in reg_group[reg]:
            print(f"+++ print log {res.dirname} ++++")
            for img_name in img_names:
                if img_name not in res.img_path_dict.keys() or len(res.img_path_dict[img_name]) == 0:
                    print("can not find", img_name)
                    continue

                paths = res.img_path_dict[img_name]
                for path in paths:
                    print(path)
                    filename = os.path.basename(path)
                    image = mpimg.imread(path)
                    # Acquire default dots per inch value of matplotlib
                    dpi = 60  # matplotlib.rcParams['figure.dpi']
                    img = image
                    # Determine the figures size in inches to fit your image
                    height, width, depth = img.shape
                    figsize = width / float(dpi), height / float(dpi)
                    plt.figure(figsize=figsize)
                    plt.title(f"{filename}")
                    plt.imshow(img)
                    plt.show()







