# -*- coding=utf-8'*-

import config
import utils
from elasticsearch import Elasticsearch

es = Elasticsearch([config.ES_HOSTS])


def query(path,size, start_ts, end_ts):
    query_json = {
        "aggs": {

        },
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "log.file.path": path
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": utils.ts2date(start_ts),
                                "lte": utils.ts2date(end_ts),
                            }
                        }

                    }
                ],
                "filter": [],
                "should": [],
                "must_not": []
            }
        }
    }

    result = es.search(index="logstash-*", body=query_json)

    result_str = ''
    for item in result["hits"]["hits"]:
        # print(item['_source']['message'])
        result_str += '%s %s\n' % (item['_source']['@timestamp'], item['_source']['message'])

    return result_str
