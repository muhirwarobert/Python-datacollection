#-*- coding=utf-8'*-
import config

import query_logs
import query_metrics

import utils

import time  # 引入time模块




fault_time = config.FAULT_TIME
exp_start = fault_time - 60 * 5
exp_end = fault_time + 60 * 5

if __name__ == '__main__':
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("当前时间戳为:", cur_time)
    # 1、创建相应的目录
    utils.mkdir("./%s" %(config.DATA_DIR))
    base_path= "./%s/%s_getdadatime_%s" %(config.DATA_DIR,config.CASE_NAME,cur_time)
    # base_path = "./%s/%s" % (config.DATA_DIR, config.CASE_NAME)
    utils.mkdir(base_path)
    base_path += "/%s_%s" % (config.CASE_TYPE,fault_time)
    print(base_path)
    utils.mkdir(base_path)


    # 2、遍历所有需要收集的日志，并写入到logs文件
    #    每个日志文件最多采集1万条数据
    base_log_path = base_path + '/log'
    utils.mkdir(base_log_path)

    for log_name in config.LOG_FILES:
        log_data = query_logs.query(log_name,10000,exp_start, exp_end)
        log_path = base_log_path + "/%s.log" % log_name
        utils.write_log(log_path,log_data)

    # 3、遍历所有需要收集的指标，并写入到csv文件
    base_metrics_path = base_path + '/metrics/'
    utils.mkdir(base_metrics_path)

    query_metrics.query_node_metrics(exp_start, exp_end, base_metrics_path)
    query_metrics.query_pod_metrics(exp_start, exp_end, base_metrics_path)
    query_metrics.query_service_metrics(exp_start, exp_end,base_metrics_path)

# 每个service的每秒处理请求数 sum(rate(istio_requests_total{destination_workload_namespace="sock-shop",reporter="destination"}[1m])) by (destination_workload )

# 每个service的延迟毫秒数总和 sum(rate(istio_request_duration_milliseconds_sum{destination_workload_namespace="sock-shop",reporter="destination"}[1m])) by (destination_workload )

# 每个service的延迟毫秒数个数 sum(rate(istio_request_duration_milliseconds_count{destination_workload_namespace="sock-shop",reporter="destination"}[1m])) by (destination_workload )

# 每个service的延迟中位数 histogram_quantile(0.50, sum(irate(istio_request_duration_milliseconds_bucket{reporter='source', destination_workload_namespace='sock-shop'}[1m])) by (destination_workload, source_workload, le))

# 响应错误数量(4xx,5xx)   sum(rate(istio_request_duration_milliseconds_sum{destination_workload_namespace="sock-shop",reporter="destination",response_code=~"^40.*|^50.*"}[1m])) by (destination_workload, source_workload )

# 响应正确数量(2xx,3xx)   sum(rate(istio_request_duration_milliseconds_sum{destination_workload_namespace="sock-shop",reporter="destination",response_code=~"^20.*|^30.*"}[1m])) by (destination_workload, source_workload )

