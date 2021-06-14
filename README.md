# Elasticsearch Private GeoIP Enrichment

Generates IP range docs for Private GeoIP Encrichment Policy

**Note - Known to be slow as sends doc per ip address, ensures unique ID per document**

## Usage

Edit lists in `locations.json` and build/run
Locations `city_name` must match Networks `name`

## ES Integrations

Create a new ingest pipeline and apply Enrichment Policy that has been created
Example `resources/geoip-info-pipeline.txt`

Use API Query to check if Enrich Event is occuring

`GET /_enrich/_stats`

## Environment Variables

| Key | Value |
|:--:|:--:|
| ELASTIC_USER | `elastic` |
| ELASTIC_PASS | `<password>` |
| ELASTIC_HOST | `<elasticsearch_host>` |
| ELASTIC_PROTO | `https`,`http` |
| ELASTIC_INDEX | `private_geoips` |
| ELASTIC_SSL_VERIFY | `True`,`False` |
| ELASTIC_SSL | `True`,`False` |
| CONFIG_FILE | `locations.json` |
| CREATE_ENRICHMENT_POLICY | `True`, `False` |
| CREATE_INDEX | `True`, `False` |

## Reference

[Elasticsearch Blog Post](https://www.elastic.co/blog/enriching-elasticsearch-data-geo-ips-internal-private-ip-addresses)
