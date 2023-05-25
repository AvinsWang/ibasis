import pickle


def dump_pkl(fpath, var_lis):
    with open(fpath, 'wb') as f:
        pickle.dump(var_lis, f)


def load_pkl(fpath):
    with open(fpath, 'rb') as f:
        return pickle.load(f)