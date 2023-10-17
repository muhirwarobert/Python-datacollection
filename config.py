#-*- coding=utf-8'*-
CASE_NAME = 'case01'
CASE_TYPE = 'normal'
FAULT_TIME = 1627565788
NAME_SPACE = 'sock-shop'

# 日志相关
ES_HOSTS = "http://192.168.9.20:9200"
LOG_FILES = [
    "sockshop-front-end",
    "sockshop-shipping",
    "sockshop-carts"
]

# 指标相关
PROM_URL = "http://192.168.9.12:30090"
PROM_METRICS_STEP = "5s"
SMOOTHING_WINDOW = 12


DATA_DIR = 'data'
METRIC_DIR = DATA_DIR + 'metrics'
LOG_DIR = DATA_DIR + 'logs'