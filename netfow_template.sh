#!/bin/bash
curl -XPUT 'localhost:9200/_template/netflow_template?pretty=true' -d '{
    "template" : "netflow-*",
    "settings": {
      "index.refresh_interval": "30s",
      "number_of_shards": "3",
      "number_of_replicas": "0"
    },
    "mappings" : {
      "_default_" : {
        "_all" : { "norms": false, "enabled": true },
        "properties" : {
          "@version": { "index": false, "type": "byte" },
          "@timestamp": { "index": true, "type": "date" },
          "netflow": {
            "dynamic": true,
            "properties": {
              "version": { "include_in_all": false, "index": false, "type": "byte" },
              "direction": { "include_in_all": false, "index": false, "type": "byte" },
              "flow_seq_num": { "include_in_all": false, "index": false, "type": "long" },
              "engine_type": { "include_in_all": false, "index": false, "type": "byte" },
              "engine_id": { "include_in_all": false, "index": false, "type": "byte" },
              "sampling_algorithm": { "include_in_all": false, "index": false, "type": "byte" },
              "sampling_interval": { "include_in_all": false, "index": false, "type": "byte" },
              "flow_sampler_id":  { "include_in_all": false, "index": false, "type": "byte" },
              "flow_records": { "include_in_all": false, "index": false, "type": "byte" },
              "flowset_id": { "include_in_all": false, "index": false, "type": "integer" },
              "ipv4_src_addr": { "index": true, "type": "ip" },
              "ipv4_dst_addr": { "index": true, "type": "ip" },
              "ipv4_next_hop": { "index": true, "type": "ip" },
              "host": { "index": true, "type": "ip" },
              "input_snmp": { "include_in_all": false, "index": false, "type": "byte" },
              "output_snmp": { "include_in_all": false, "index": false, "type": "byte" },
              "in_pkts": { "include_in_all": false, "index": true, "type": "long" },
              "in_bytes": { "include_in_all": false, "index": true, "type": "long" },
              "first_switched": { "include_in_all": false, "index": false, "type": "date" },
              "last_switched": { "include_in_all": false, "index": false, "type": "date" },
              "l4_src_port": { "index": true, "type": "integer" },
              "l4_dst_port": { "index": true, "type": "integer" },
              "tcp_flags": { "include_in_all": false, "index": false, "type": "integer" },
              "protocol": { "include_in_all": false, "index": true, "type": "short" },
              "src_tos": { "include_in_all": false, "index": false, "type": "integer" },
              "src_as": { "index": true, "type": "integer" },
              "dst_as": { "index": true, "type": "integer" },
              "src_mask": { "include_in_all": false, "index": false, "type": "byte" },
              "dst_mask": { "include_in_all": false, "index": false, "type": "byte" },
              "netflow.ipv4_dst_prefix": { "include_in_all": false, "index": false, "type": "ip" },
              "netflow.ipv4_src_prefix": { "include_in_all": false, "index": false, "type": "ip" },
              "bgp_ipv4_next_hop": { "include_in_all": false, "index": false, "type": "ip" }
            }
          }
        }
      }
    }
  }'
