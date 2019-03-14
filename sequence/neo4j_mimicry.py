#!/usr/bin/env python3

import sys
import os
from multiprocessing import Pool
from contextlib import closing

from neo4jrestclient.client import GraphDatabase

# Process each sample
def mimicry(folder,h,neo4j_username,neo4j_password,attack_features,generations):
    # Connect to Neo4j database
    neo4j_db = GraphDatabase('http://localhost:7474', username=neo4j_username, password=neo4j_password)

    # Create cache so we can prevent duplicate queries for this sample
    cache = dict()

    seq = list()

    # Read in sample's sequence
    with open(os.path.join(folder,h),'r') as fr:
        for line in fr:
            line = line.strip('\n')
            seq.append(line)

    # Holds final attack sequence(s)
    attack = [list() for n in range(generations)]

    # Run sample through Mimicry attack

    # For each pair of API calls
    for i in range(len(seq)-1):
        # Get api calls
        api1 = seq[i].split(' ')[1]
        api2 = seq[i+1].split(' ')[1]

        # Append api call along with program counter
        for a in attack:
            a.append(seq[i])

        # If we've already queried this path, just get path
        key = '{0},{1}'.format(api1,api2)
        if key in cache:
            result = cache[key]
        # Else, query Neo4j for path
        else:
            q =  "MATCH (n:NODE {{name: '{0}'}}) MATCH (m:NODE {{name: '{1}'}}) ".format(api1,api2)
            # Get path of exactly length 2
            q += "MATCH path=(n)-[:EDGE*2]->(m) "
            # Return first n paths
            q += "RETURN extract(node in nodes(path) | node.name) as nodes LIMIT {0}".format(generations)

            result = neo4j_db.query(q)

            # Cache result
            cache[key] = result

        # From result, extend paths
        for e,r in enumerate(result):
            api = r[0][1]
            # We put -1 in the PC place so we know that this is the call we inserted
            attack[e].append('-1 {0}'.format(api))

    # Write final attack sequence(s) to folder
    for e,a in enumerate(attack):
        with open(os.path.join(attack_features,h,str(e)),'w') as fw:
            for api in a:
                fw.write('{0}\n'.format(api))

            # Append final api call
            fw.write('{0}\n'.format(seq[-1]))

def mimicry_wrapper(args):
    return mimicry(*args)

def usage():
    print('usage: python3 neo4j_mimicry.py neo4j_username neo4j_password target_hashes.txt sequences/ attack-features/ n_attack_generations')
    sys.exit(2)

def _main():
    if len(sys.argv) != 7:
        usage()

    neo4j_username = sys.argv[1]
    neo4j_password = sys.argv[2]
    targets = sys.argv[3]
    sequences = sys.argv[4]
    attack_features = sys.argv[5]
    generations = int(sys.argv[6])

    # Get hashes to perform attack on
    hashes = list()
    with open(targets,'r') as fr:
        for line in fr:
            line = line.strip('\n')
            hashes.append(line)

        # Create output folders
        folder = os.path.join(attack_features,line)
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Create arguments for multiprocessing
    args = [(sequences,h,neo4j_username,neo4j_password,attack_features,generations) for h in hashes]

    # Perform attack
    with closing ( Pool(20,maxtasksperchild=1) ) as p:
        results = p.imap_unordered(mimicry_wrapper,args)

        for e,r in enumerate(results):
            sys.stdout.write('Generating attack samples: {0}/{1}\r'.format(e+1,len(args)))
            sys.stdout.flush()

        sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == '__main__':
    _main()
