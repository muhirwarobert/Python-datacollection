# -*- coding=utf-8'*-
import os
import config
import requests
from datetime import datetime
import pandas as pd


def mkdir(path):
    if os.path.exists(path):
        return
    os.mkdir(path)


def write_log(path, data):
    try:
        f = open(path, "w")
        f.write(data)
        print("%s log file write success!" % path)
    finally:
        f.flush()
        f.close()


def query_range_prom_data(query, start, end, step=config.PROM_METRICS_STEP, instant=False):
    """
    query over a range of time or instant
    :param instant: <bool> whether to execute instant query
    :param query: <string> Prometheus expression query string.
    :param start: <rfc3339 | unix_timestamp> Start timestamp.
    :param end: <rfc3339 | unix_timestamp> End timestamp.
    :param step: <duration | float> Query resolution step width in duration format or float number of seconds.
    :return: list of query result
    """
    if instant:
        prom_url = config.PROM_URL + "/api/v1/query"
        params = {
            "query": query
        }
    else:
        prom_url = config.PROM_URL + "/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
    resp = requests.post(url=prom_url, data=params)
    return resp.json()


# 指标查询结果转为dataframe,保存到csv中
def write_metric_data(values, filename):
    values = list(zip(*values))
    df = pd.DataFrame()
    df['timestamp'] = values[0]
    df['timestamp'] = df['timestamp'].astype('datetime64[s]')
    df['value'] = pd.Series(values[1])
    df['value'] = df['value'].astype('float64')
    df.set_index('timestamp')
    df.to_csv(filename)


# 时间戳转零时区格式字符串
def ts2date(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S.000Z')
