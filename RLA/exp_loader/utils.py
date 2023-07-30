
def _archive_tester_query(data_root, task_table_name, reg, log_type):
    experiment_data_dict = {}
    root_dir_regex = osp.join(data_root, log_type, task_table_name, reg)
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