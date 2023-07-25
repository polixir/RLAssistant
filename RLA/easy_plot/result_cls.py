# Created by xionghuichen at 2023/7/3
# Email: chenxh@lamda.nju.edu.cn


class Result:
    def __init__(self, hyper_param=None, dirname=None):
        self.hyper_param = hyper_param
        self.dirname = dirname


class CsvResult(Result):
    def __init__(self, monitor=None, progress=None, dirname=None, metadata=None, hyper_param=None):
        super(CsvResult, self).__init__(hyper_param=hyper_param, dirname=dirname)
        self.monitor = monitor
        self.progress = progress
        self.metadata = metadata


class ImgResult(Result):
    def __init__(self, hyper_param=None, dirname=None, img_path_dict=None):
        super(ImgResult, self).__init__(hyper_param=hyper_param, dirname=dirname)
        self.img_path_dict = img_path_dict
