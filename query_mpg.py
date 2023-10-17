
import utils
import pandas as pd
# 创建mpg
def generate_mpg_data(data_dir):
    df = pd.DataFrame(columns=['source', 'destination'])
    query_arr = [["source_workload", "destination_workload", "service", "service",
                  "sum(istio_tcp_received_bytes_total) by (source_workload, destination_workload)"],
                 ["source_workload", "destination_workload", "service", "service",
                  "sum(istio_requests_total{destination_workload_namespace=\'sock-shop\'}) "
                  "by (source_workload, destination_workload)"],
                 ["pod", "instance", "container", "host",
                  "sum(container_cpu_usage_seconds_total{namespace=\"sock-shop\", "
                  "container!~\"POD|istio-proxy|\"}) by (instance, pod)"],
                 ["instance", "pod", "host", "container",
                  "sum(container_cpu_usage_seconds_total{namespace=\"sock-shop\", "
                  "container!~\"POD|istio-proxy|\"}) by (instance, pod)"],
                 ["kubernetes_pod_name", "source_workload", "container", "service",
                  "sum(istio_requests_total{destination_workload_namespace='sock-shop', reporter='source'})"
                  " by (kubernetes_pod_name, source_workload)"],
                 ["source_workload", "kubernetes_pod_name", "service", "container",
                  "sum(istio_requests_total{destination_workload_namespace='sock-shop', reporter='source'})"
                  " by (kubernetes_pod_name, source_workload)"],
                 ["kubernetes_pod_name", "destination_workload", "container", "service",
                  "sum(istio_requests_total{destination_workload_namespace='sock-shop', reporter='destination'})"
                  " by (kubernetes_pod_name, destination_workload)"],
                 ["destination_workload", "kubernetes_pod_name", "service", "container",
                  "sum(istio_requests_total{destination_workload_namespace='sock-shop', reporter='destination'})"
                  " by (kubernetes_pod_name, destination_workload)"],
                 ["kubernetes_pod_name", "source_workload", "container", "service",
                  "sum(istio_tcp_received_bytes_total{destination_workload_namespace='sock-shop', reporter='source'})"
                  " by (kubernetes_pod_name, source_workload)"],
                 ["source_workload", "kubernetes_pod_name", "service", "container",
                  "sum(istio_tcp_received_bytes_total{destination_workload_namespace='sock-shop', reporter='source'})"
                  " by (kubernetes_pod_name, source_workload)"],
                 ["kubernetes_pod_name", "destination_workload", "container", "service",
                  "sum(istio_tcp_received_bytes_total{destination_workload_namespace='sock-shop', "
                  "reporter='destination'}) by (kubernetes_pod_name, destination_workload)"],
                 ["destination_workload", "kubernetes_pod_name", "service", "container",
                  "sum(istio_tcp_received_bytes_total{destination_workload_namespace='sock-shop', "
                  "reporter='destination'}) by (kubernetes_pod_name, destination_workload)"],
                 ]
    for query_info in query_arr:
        results = utils.query_range_prom_data(query_info[-1], None, None, instant=True)['data']['result']
        for result in results:
            metric = result['metric']
            source = metric[query_info[0]]
            destination = metric[query_info[1]]
            df = df.append({'source': source + '_' + query_info[2],
                            'destination': destination + '_' + query_info[3]}, ignore_index=True)
    df = df.drop_duplicates()
    df.to_csv(data_dir + '_mpg.csv')
