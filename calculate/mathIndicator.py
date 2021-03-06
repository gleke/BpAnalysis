import math
import numpy as np


"""
这个是一个统计学文件

专门计算各种不同的统计学量  
如 mse / rmse / mae / sd

"""

def transfer_list(records_real, records_predict):
    return list(records_real), list(records_predict)


def get_mse(records_real, records_predict):
    """
    均方误差 估计值与真值 偏差
    """
    records_real, records_predict = transfer_list(records_real, records_predict)
    if len(records_real) == len(records_predict):
        return sum([(x - y) ** 2 for x, y in zip(records_real, records_predict)]) / len(records_real)
    else:
        return None


def get_rmse(records_real, records_predict):
    """
    均方根误差：是均方误差的算术平方根
    """
    records_real, records_predict = transfer_list(records_real, records_predict)
    mse = get_mse(records_real, records_predict)
    if mse:
        return math.sqrt(mse)
    else:
        return None


def get_mae(records_real, records_predict):
    """
    平均绝对误差
    """
    records_real, records_predict = transfer_list(records_real, records_predict)
    if len(records_real) == len(records_predict):
        return sum([abs(x - y) for x, y in zip(records_real, records_predict)]) / len(records_real)
    else:
        return 10000


def get_sd(records_real, records_predict):
    """
    sd
    """
    records_real = np.asarray(records_real)
    records_predict = np.asarray(records_predict)
    diff = records_real - records_predict
    return np.std(diff, axis=0)