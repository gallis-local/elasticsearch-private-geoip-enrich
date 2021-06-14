#!/usr/bin/python3
import os
import json
import ipaddress
from typing import Mapping
from elasticsearch import Elasticsearch,RequestsHttpConnection

## ENV VARS

elasticsearch_user = os.getenv("ELASTIC_USER", "elastic")
elasticsearch_pass = os.getenv("ELASTIC_PASS")
elasticsearch_host = os.getenv("ELASTIC_HOST")
elasticsearch_proto = os.getenv("ELASTIC_PROTO", "https")
elasticsearch_index = os.getenv("ELASTIC_INDEX", "private_geoips")
elasticsearch_ssl_verify = os.getenv("ELASTIC_SSL_VERIFY", True)
elasticsearch_ssl = os.getenv("ELASTIC_SSL", True)
config_file_name = os.getenv("CONFIG_FILE", "locations.json")
create_enrichment_policy = os.getenv("CREATE_ENRICHMENT_POLICY", True)
create_index = os.getenv("CREATE_INDEX", True)

## INIT

es = Elasticsearch([elasticsearch_proto + "://" + elasticsearch_user + ":" + elasticsearch_pass + "@" + elasticsearch_host], connection_class=RequestsHttpConnection, use_ssl=elasticsearch_ssl, verify_certs=elasticsearch_ssl_verify)


## FUNCTIONS
def init_policy():
    policy_name = elasticsearch_index + "_policy"
    policy_body = { 
        "match": { 
            "indices": "private_geoips", 
            "match_field": "source.ip", 
            "enrich_fields": ["city_name", "continent_name", "country_iso_code", "country_name", "location"] 
        } 
    }
    if es.enrich.get_policy(name=policy_name)["policies"] == []:
        print("Creating Policy...")
        es.enrich.put_policy(name=policy_name, body=policy_body)
        print("Policy Created - " + policy_name)
        print("Execute Policy Update...")
        es.enrich.execute_policy(name=policy_name)
        print("Executed Policy - " + policy_name)
    else:
        print("Policy Exists - " + policy_name)
    return

def init_index(index):
  index_mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": { 
            "properties": { 
                "city_name": { 
                    "type": "text" 
                }, 
                "continent_name": { 
                    "type": "text" 
                }, 
                "country_iso_code": { 
                    "type": "text" 
                }, 
                "country_name": { 
                    "type": "text" 
                }, 
                "location": { 
                    "type": "geo_point" 
                }, 
                "source.ip": { 
                    "type": "ip" 
                } 
            } 
        } 
    }
  if es.indices.exists(index=index):
    print("Index Exists - " + index)
  else:
    print("Creating Index...")      
    es.indices.create(index=index, body=index_mapping)
    print("Created Index - " + index)
  return 

def send_to_elastic(data, location, index):
    """ Send docs to Elasticsearch"""
    res = es.index(index=index,id=location, body=data)
    print(location + " | " + str(res))
    return res

def get_location(ip, networks, locations):
    json_obj = {}
    for network in networks:
        if ipaddress.ip_address(ip) in network["network"]:
            for location in locations:
                if network["name"] == location["city_name"]:
                    json_obj = location
                    json_obj["source_ip"] = ip
                    continue
        continue
    return json_obj

def generate_entries(networks, locations):
    for network in networks:
        ips_list = network["network"]
        for i in ips_list:
            i = str(i)
            location = network["_id"] + "-" + i
            json_obj = get_location(i, networks, locations)
            send_to_elastic(json_obj, location, elasticsearch_index)
        print(network["name"])

def main():

    print("----Reading Config-----")

    # Read Config JSON
    config_file = open(config_file_name)
    location_data = json.load(config_file)
    config_file.close()

    print("----Generating Networks-----")

    # Create IP Ranges
    for network in location_data["networks"]:
        network["network"] = ipaddress.ip_network(network['network'])
    locations = location_data["locations"]
    networks = location_data["networks"]

    print("----Using Locations-----")

    # Print Location JSON
    for item in networks:
        print(item)

    print("----Using Networks-----")

    # Print Network JSON
    for item in networks:
        print(item)

    if create_index:
        print("----Index Configuration-----")
        init_index(elasticsearch_index)
    else:
        pass

    if create_enrichment_policy:
        print("----Enrichment Policy------")
        init_policy()
    else:
        pass
    
    print("----Generating Entries------")

    # Generates GEOIP docs for ranges
    generate_entries(networks, locations)

    print("----Completed----")
    print("Final steps will be to create the Enrichment section in the ingest pipeline of your choice")

    
main()