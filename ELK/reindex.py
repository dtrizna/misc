#!/usr/bin/env python

import sys
import getopt
import elasticsearch
import elasticsearch.helpers


def usage():

        global __name__
        print("Usage:")
        print("\tpython {} [options]".format(sys.argv[0]))
        print("Options:")
        print("""
        -i, --index [name]      - will ask ElasticSearch server to reindex this index to new one based on current
                                  template. Will name new index as [name].reindexed

Disclaimer! BE SURE THAT CORRECT TEMPLATE IS CONFIGURED.
Use template_curl.sh for that!""")


def main():

        try:
                opts, args = getopt.getopt(sys.argv[1:], "i:h", ["index", "help"])
        except getopt.GetoptError as geterr:
                def error():
                        print("Error message: {}.\nPlease refer to '{} --help'.".format(geterr, sys.argv[0]))
                return error()

        if not len(sys.argv[1:]):
                usage()


        for o,a in opts:
                if o in ["-i", "--index"]:

                        print("Source index is {}!".format(a))
                        b = a + ".reindexed"
                        print("New index will be named {}".format(b))
                        elasticSource = elasticsearch.Elasticsearch([{"host": "localhost", "port": 9200}], request_timeout=300)
                        elasticDest = elasticsearch.Elasticsearch([{"host": "localhost", "port": 9200}], request_timeout=300)
                        elasticsearch.helpers.reindex(client=elasticSource, source_index=a, target_index=b, target_client=elasticDest, chunk_size=50)

                elif o in ["-h", "--help"]:
                        return usage()
                else:
                        assert False, "Incorrect option.\nPlease refer to '{} --help'.".format(sys.argv[0])

main()
