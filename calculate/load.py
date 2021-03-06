import xgboost as xgb
from sklearn.model_selection import train_test_split

from data_pipline import *
from load_file import SensorData


# 加载指标值
# 70是代表老数据  新数据统一用24


def create_table(name):
    if name == '70':
        indicator = pd.read_table('../scene/record/indicators.txt', header=None)
        record = pd.read_table('../scene/record/test_log.txt', header=None)
        indicator.columns = ['name', 'ptt', 'vally_ptt', 'rr1', 'rr2', 'sum1', 'up1', 'down1', 'sum2', 'up2', 'down2']
        record.columns = ['idx', 'stu', 'name', 'h1', 'l1', 'h2', 'l2']
        h, l = [], []
        for i in range(record.shape[0]):
            h.append(int((int(record.loc[i, 'h1']) + int(record.loc[i, 'h2'])) / 2))
            l.append(int((int(record.loc[i, 'l1']) + int(record.loc[i, 'l2'])) / 2))
        record['h1'] = h
        record['l1'] = l
        df = pd.merge(indicator, record, on='name')
        df = df[['name', 'ptt', 'vally_ptt', 'rr1', 'rr2', 'sum1', 'up1', 'down1', 'sum2', 'up2', 'down2', 'h1', 'l1']]
        df = df.rename(columns={"h1": "high", "l1": "low"})
        return df
    else:
        sensor = SensorData()
        record = sensor.record
        if name == '24':
            ids = sensor.get_record_number()
        else:
            ids = list(sensor.load_patined_idx())
        metric_name = ['bf', 'bs', 'sd', 'df', 'sf', 'rr', 'asd', 'asf', 'ptt']
        columns = ['bf', 'bs', 'sd', 'df', 'sf', 'rr', 'asd', 'asf', 'ptt', 'high', 'low']
        df = pd.DataFrame(columns=columns)
        for k in ids:
            metric = sensor.load_json_metric(k)
            high, low = int(record[record['number'] == k]['high']), int(record[record['number'] == k]['low'])
            l = []
            for name in metric_name:
                values = metric[name]
                l.append(get_metric_value(values))
            if sum(l) == 0:
                continue
            l.append(high)
            l.append(low)
            insert_row = dict(zip(columns, l))
            df.loc[df.shape[0]] = insert_row
        df['ptt'] = [abs(_) for _ in list(df['ptt'])]
        return df


def load(name='70', bp='high', ratio=0.5):
    if name == 'patient':
        from data_pipline.patient import load_metric
        all, k, m, h, l = load_metric()
        df = all
    else:
        df = create_table(name)
    if name == '70':
        train_X, test_X, train_Y, test_Y = train_test_split(
            df[['ptt', 'vally_ptt', 'rr1', 'rr2', 'sum1', 'up1', 'down1', 'sum2', 'up2', 'down2']], df[bp],
            test_size=ratio)
        return train_X, test_X, train_Y, test_Y
    else:
        train_X, test_X, train_Y, test_Y = train_test_split(
            df[['bf', 'bs', 'sd', 'df', 'sf', 'rr', 'asd', 'asf', 'ptt']], df[bp], test_size=ratio)
        return train_X, test_X, train_Y, test_Y


def load_all(name='24'):
    df = create_table(name)
    high, low = df.loc[:, 'high'], df.loc[:, 'low']
    if name == '70':
        df = df.drop(['name', 'high', 'low'], axis=1)
    else:
        df = df.drop(['high', 'low'], axis=1)
    df.fillna(0, inplace=True)
    return df, xgb.DMatrix(df), list(high), list(low)


def dump_value(a, b, name):
    l = len(a)
    with open('../scene/result/' + name + '.txt', 'w') as f:
        for i in range(l):
            inp = str(a[i]) + ',' + str(b[i]) + '\n'
            f.writelines(inp)


def load_metric(key='70', model='ga_xgboost'):
    if key == '':
        base = '../scene/result/' + model
    else:
        base = '../scene/result/' + model + '_'
    file1 = base + key + '_high.txt'
    file2 = base + key + '_low.txt'
    ph, rh, pl, rl = [], [], [], []
    with open(file1, 'r') as f:
        lines = f.readlines()
        for line in lines:
            p, r = line.split(',')
            ph.append(int(p))
            rh.append(int(r))
    with open(file2, 'r') as f:
        lines = f.readlines()
        for line in lines:
            p, r = line.split(',')
            pl.append(int(p))
            rl.append(int(r))

    # 去除异常值
    # i1, i2 = [],[]
    # for i in range(len(ph)):
    #     if abs(ph[i]-rh[i]) > 30:
    #         i1.append(ph[i])
    #         i2.append(rh[i])
    # for k,d in zip(i1,i2):
    #     ph.remove(k)
    #     rh.remove(d)

    return ph, rh, pl, rl


def get_metric_value(valeus):
    l = len(valeus)
    ret = 0.0
    cnt = 0
    for i in range(int(0.6 * l)):
        if valeus[i] != 0:
            ret += valeus[i]
            cnt += 1
    if cnt == 0:
        return 0
    else:
        return ret / cnt


if __name__ == '__main__':
    tb = create_table('patient')
    print(tb)
