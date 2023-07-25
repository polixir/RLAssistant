# Created by xionghuichen at 2023/2/2
# Email: chenxh@lamda.nju.edu.cn

from test._base import BaseTest
from RLA.easy_plot.plot_func_v2 import plot_func
from RLA.easy_plot.plot_saved_images import plot_saved_images
import os


class ScriptTest(BaseTest):
    def _init_baisc_info(self):
        self.data_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data_root')
        self.task = 'demo_task'

    def test_multiply_metric(self):
        self._init_baisc_info()
        regs = [
            '2022/11/24/*',
            '2023/02/02/*',
        ]

        _ = plot_func(data_root=self.data_root, task_table_name=self.task, regs=regs, split_keys=['learning_rate'],
                      metrics=['perf/mse', 'y_out', 'y_out_std', 'y_out_max'], pretty=False)

    def test_pretty_multiply_metric(self):
        self._init_baisc_info()
        regs = [
            '2022/11/24/*',
            '2023/02/02/*',
        ]

        _ = plot_func(data_root=self.data_root, task_table_name=self.task, regs=regs, split_keys=['learning_rate'],
                      metrics=['perf/mse', 'y_out', 'y_out_std'], use_marker=True, resample=100,
                      regs2legends=['lr=0.001', 'lr=0.0001'],
                      ylabel=['MSE', 'Y', 'Y std'], pretty=True, legend_ncol=4, save_name='multi_plot.pdf')


    def test_log_filter(self):
        self._init_baisc_info()
        regs = [
            '2022/03/01/21-[12]*'
        ]
        _ = plot_func(data_root=self.data_root, task_table_name=self.task, regs=regs, split_keys=['learning_rate'],
                      metrics=['perf/mse', 'y_out', 'y_out_std'], use_marker=True, resample=100,
                      hp_filter_dict={'learning_rate': ['0.001', '0.01']}, ylabel=['MSE', 'Y', 'Y std'],
                      pretty=True, legend_ncol=4, verbose=True)


    def test_result_plot(self):
        self._init_baisc_info()
        regs = [
            '2022/03/01/21-[12]*'
        ]
        _ = plot_saved_images(data_root=self.data_root, task_table_name=self.task, regs=regs, img_names=['*react_func.png'], verbose=True)

