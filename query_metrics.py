# -*- coding=utf-8'*-

import config
import utils

import pandas as pd


# 查询节点相关的指标
def query_node_metrics(start_ts, end_ts, metrics_dir):
    # 节点发包率，顺便获取节点名称
    net_query = "irate(node_network_transmit_packets_total{device='eth0', job='kubernetes-service-endpoints'}[1m])"
    print("所有节点网络发送：" + net_query)
    net_data_arr = utils.query_range_prom_data(net_query, start_ts, end_ts)['data']['result']
    for net_data in net_data_arr:
        instance = net_data['metric']['instance']
        node_name = net_data['metric']['kubernetes_node']
        data_dir = metrics_dir + 'host/'
        utils.mkdir(data_dir)
        utils.write_metric_data(net_data['values'], data_dir + node_name + '_host_net_transmit.csv')

        # 节点网络接收
        query = "irate(node_network_receive_packets_total{device='eth0',instance='%s'}[1m])" % (instance)
        print(node_name+"节点网络接收："+query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_host_net_receive.csv')

        # 节点磁盘读速度
        query = "irate(node_disk_read_bytes_total{device=~'sd.*',instance='%s'}[1m])/1024/1024" % (instance)
        print(node_name + "节点磁盘读速度：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_disk_read_byte.csv')

        # 节点磁盘读速度
        query = "irate(node_disk_written_bytes_total{device=~'sd.*',instance='%s'}[1m])/1024/1024" % (instance)
        print(node_name + "节点磁盘写入速度：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_disk_written_bytes.csv')


        # 节点cpu使用率
        query = "sum(rate(node_cpu_seconds_total{mode != 'idle',  mode!= 'iowait', mode!~'^(?:guest.*)$', " \
                "instance='%s', job='kubernetes-service-endpoints' }[1m])) / " \
                "count(node_cpu_seconds_total{mode='system', instance='%s'," \
                " job='kubernetes-service-endpoints'})" % (instance, instance)
        print(node_name+"节点cpu使用率：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_host_cpu_usage.csv')

        # 节点内存使用率
        query = "1 - (node_memory_MemFree_bytes{instance='%s', job='kubernetes-service-endpoints'}+node_memory_Cached_bytes{instance='%s', job='kubernetes-service-endpoints'}+node_memory_Buffers_bytes{instance='%s', job='kubernetes-service-endpoints'}) / " \
                "node_memory_MemTotal_bytes{instance='%s', job='kubernetes-service-endpoints'}" % (
                    instance, instance, instance, instance)
        print(node_name+"节点内存使用率：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_host_mem_usage.csv')

        # 节点系统负载1分钟平均 uptime
        query = "node_load1{instance='%s'}" % (instance)
        print(node_name + "系统负载1分钟平均：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_node_load1.csv')


        # 节点系统负载5分钟平均
        query = "node_load5{instance='%s'}" % (instance)
        print(node_name + "系统负载5分钟平均：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result'][0]
        utils.write_metric_data(data['values'], data_dir + node_name + '_node_load5.csv')


# 查询运行的pod相关的指标(CPU使用率、内存使用率、网络流量)
def query_pod_metrics(start_ts, end_ts, metrics_dir):
    # pod cpu使用率
    query = "sum(rate(container_cpu_usage_seconds_total{namespace='" + config.NAME_SPACE + "', container!~'POD|istio-proxy|'}[1m]" \
            ")) by (pod, container)"

    print("所有Container CPU使用率：" +query)
    cpu_data_arr = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result']
    for cpu_data in cpu_data_arr:
        # svc = cpu_data['metric']['container']
        pod_name = cpu_data['metric']['pod']
        data_dir = metrics_dir  + 'container/'
        utils.mkdir(data_dir)
        utils.write_metric_data(cpu_data['values'], data_dir + pod_name + '_container_cpu.csv')
        # pod 内存使用率
        query = "container_memory_rss{namespace='%s', pod='%s',container!~'POD|istio-proxy|'}/container_spec_memory_limit_bytes{namespace='%s', pod='%s', container!~'POD|istio-proxy|'}" % (config.NAME_SPACE, pod_name,config.NAME_SPACE, pod_name)
        print(pod_name + "内存使用率：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_mem.csv')
        # pod网络输出字节数
        query = "sum(rate(container_network_transmit_packets_total{namespace='%s', pod='%s'}[1m]))/1024 "  % (config.NAME_SPACE,pod_name)
        print(pod_name + "网络发送包数量(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_net_transmit_packets.csv')

        # pod网络接收字节数
        query = "sum(rate(container_network_receive_packets_total{namespace='%s', pod='%s'}[1m])) /1024 "  % (config.NAME_SPACE, pod_name)
        print(pod_name + "网络接收包数量(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_net_receive_packets.csv')

        # pod网络输出字节数
        query = "sum(rate(container_network_transmit_bytes_total{namespace='%s', pod='%s'}[1m]))/1024 " % (
        config.NAME_SPACE, pod_name)
        print(pod_name + "网络发送字节数量(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_net_transmit_bytes.csv')

        # pod网络接收字节数
        query = "sum(rate(container_network_receive_bytes_total{namespace='%s', pod='%s'}[1m])) /1024 " % (
        config.NAME_SPACE, pod_name)
        print(pod_name + "网络接收字节数量(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_net_receive_bytes.csv')

        # pod文件系统读取字节数
        query = "sum(rate(container_fs_reads_bytes_total{namespace='%s', pod='%s',image!=''}[1m])) without (device) " % (
            config.NAME_SPACE, pod_name)
        print(pod_name + "文件系统读取字节数(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        if len(data['data']['result']):
            utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_fs_reads_bytes.csv')

        # pod文件系统读取字节数
        query = "sum(rate(container_fs_writes_bytes_total{namespace='%s', pod='%s',image!=''}[1m]))  without (device)" % (
            config.NAME_SPACE, pod_name)
        print(pod_name + "文件系统写入字节数(k)：" + query)
        data = utils.query_range_prom_data(query, start_ts, end_ts)
        if len(data['data']['result']):
            utils.write_metric_data(data['data']['result'][0]['values'], data_dir + pod_name + '_container_fs_writes_bytes.csv')


# 查询服务相关的指标（）
def query_service_metrics(start_ts, end_ts, metrics_dir):

    data_dir = metrics_dir + '/service/'
    utils.mkdir(data_dir)

    # 50%时延
    # source
    source_latency_df = pd.DataFrame()
    query = "histogram_quantile(0.50, sum(irate(istio_request_duration_milliseconds_bucket{reporter='source', " \
            "destination_workload_namespace='" + config.NAME_SPACE + "'}[1m])) by (destination_workload, source_workload, le)) / 1000"
    print("服务查询1："+query)
    results = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result']
    for result in results:
        dest_svc = result['metric']['destination_workload']
        src_svc = result['metric']['source_workload']
        name = src_svc + '_' + dest_svc
        values = result['values']

        values = list(zip(*values))
        if 'timestamp' not in source_latency_df:
            timestamp = values[0]
            source_latency_df['timestamp'] = timestamp
            source_latency_df['timestamp'] = source_latency_df['timestamp'].astype('datetime64[s]')
        metric = values[1]
        source_latency_df[name] = pd.Series(metric)
        source_latency_df[name] = source_latency_df[name].astype('float64') * 1000

    # 数据不完整的用下面的方式去填充
    query = "sum(irate(istio_tcp_sent_bytes_total{reporter='source'}[1m])) " \
            "by (destination_workload, source_workload) / 1000"
    print("服务查询2：" + query)
    results = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result']
    for result in results:
        dest_svc = result['metric']['destination_workload']
        src_svc = result['metric']['source_workload']
        name = src_svc + '_' + dest_svc
        values = result['values']
        values = list(zip(*values))
        if 'timestamp' not in source_latency_df:
            timestamp = values[0]
            source_latency_df['timestamp'] = timestamp
            source_latency_df['timestamp'] = source_latency_df['timestamp'].astype('datetime64[s]')
        metric = values[1]
        source_latency_df[name] = pd.Series(metric)
        source_latency_df[name] = source_latency_df[name].astype('float64'). \
            rolling(window=config.SMOOTHING_WINDOW, min_periods=1).mean()

    filename = data_dir + 'services_latency_source_50.csv'
    source_latency_df = source_latency_df.set_index(['timestamp'])
    source_latency_df.to_csv(filename)

    # destination
    dest_latency_df = pd.DataFrame()
    query = "histogram_quantile(0.50, sum(irate(istio_request_duration_milliseconds_bucket{reporter='destination', " \
            "destination_workload_namespace='" + config.NAME_SPACE + "'}[1m])) by (destination_workload, source_workload, le)) / 1000"
    print("服务查询3：" + query)
    results = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result']
    for result in results:
        dest_svc = result['metric']['destination_workload']
        src_svc = result['metric']['source_workload']
        name = src_svc + '_' + dest_svc
        values = result['values']
        values = list(zip(*values))
        if 'timestamp' not in dest_latency_df:
            timestamp = values[0]
            dest_latency_df['timestamp'] = timestamp
            dest_latency_df['timestamp'] = dest_latency_df['timestamp'].astype('datetime64[s]')
        metric = values[1]
        dest_latency_df[name] = pd.Series(metric)
        dest_latency_df[name] = dest_latency_df[name].astype('float64') * 1000

    # 数据不完整的用下面的方式去填充
    query = "sum(irate(istio_tcp_sent_bytes_total{reporter='destination'}[1m])) " \
            "by (destination_workload, source_workload) / 1000"
    print("服务查询4：" + query)
    results = utils.query_range_prom_data(query, start_ts, end_ts)['data']['result']
    for result in results:
        dest_svc = result['metric']['destination_workload']
        src_svc = result['metric']['source_workload']
        name = src_svc + '_' + dest_svc
        values = result['values']

        values = list(zip(*values))
        if 'timestamp' not in dest_latency_df:
            timestamp = values[0]
            dest_latency_df['timestamp'] = timestamp
            dest_latency_df['timestamp'] = dest_latency_df['timestamp'].astype('datetime64[s]')
        metric = values[1]
        dest_latency_df[name] = pd.Series(metric)
        dest_latency_df[name] = dest_latency_df[name].astype('float64'). \
            rolling(window=config.SMOOTHING_WINDOW, min_periods=1).mean()

    filename = data_dir + 'services_latency_destination_50.csv'
    dest_latency_df = dest_latency_df.set_index(['timestamp'])
    dest_latency_df.to_csv(filename)
    return source_latency_df, dest_latency_df
