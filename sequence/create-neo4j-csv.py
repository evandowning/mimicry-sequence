#!/usr/bin/env python3

import sys
import os

# Exports graph to Neo4j CSV files to be imported into Neo4j
def export_graph(graph,output):

    with open(output,'w') as fw:

        # Iterate through graph and write to output file
        e = 0
        for k,v in graph.items():
            sys.stdout.write('Nodes {0}/{1}\r'.format(e+1,len(list(graph.keys()))))
            sys.stdout.flush()

            for c in v:
                fw.write('"{0}","{1}"\n'.format(k,c))

            e += 1

    sys.stdout.write('\n')
    sys.stdout.flush()

# Creates graph structure
def create_graph(folder,samples):
    rv = dict()

    for e,s in enumerate(samples):
        sys.stdout.write('Samples {0}/{1}\r'.format(e+1,len(samples)))
        sys.stdout.flush()

        # Get sample sequence
        with open(os.path.join(folder,s),'r') as fr:
            previous = None
            for line in fr:
                line = line.strip('\n')
                pc,api = line.split(' ')

                # Build graph
                if previous != None:
                    if previous not in rv:
                        rv[previous] = set()

                    rv[previous].add(api)

                previous = api

    sys.stdout.write('\n')
    sys.stdout.flush()

    return rv

def usage():
    print('usage: python3 create-neo4j-csv.py sequences/ classes.txt class_name output.csv')
    sys.exit(2)

def _main():
    if len(sys.argv) != 5:
        usage()

    folder = sys.argv[1]
    classes = sys.argv[2]
    class_name = sys.argv[3]
    output = sys.argv[4]

    samples = list()
    # Get hashes we care about
    with open(classes,'r') as fr:
        for line in fr:
            line = line.strip('\n')
            h,l = line.split('\t')

            if l == class_name:
                samples.append(h)

    print('Creating graph...')

    # Create structure of graph
    graph = create_graph(folder,samples)

    print('Exporting to CSV files')

    # Export sequences to CSV files
    export_graph(graph,output)

if __name__ == '__main__':
    _main()
