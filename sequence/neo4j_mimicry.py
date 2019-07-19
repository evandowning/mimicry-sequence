#!/usr/bin/env python3

import os
import random

from neo4jrestclient.client import GraphDatabase

# Process each sample
def mimicry(folder,h,neo4j_username,neo4j_password,attack_features,generations,preferred):
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
    attack = ['']*generations

    # Will hold final API call to append to attacks
    last = None

    # Run sample through Mimicry attack

    # For each pair of API calls
    for i in range(len(seq)-1):
        # Get api calls
        api1 = seq[i].split(' ')[1]
        api2 = seq[i+1].split(' ')[1]

        last = seq[i+1]

        # Insert API call for each attack
        if len(attack[0]) == 0:
            for a in range(len(attack)):
                attack[a] = seq[i]
        else:
            for a in range(len(attack)):
                attack[a] += ';{0}'.format(seq[i])

        result = list()

        # If we've already queried this path, just get path
        key = '{0},{1}'.format(api1,api2)
        if key in cache:
            result = cache[key]

        # Else, query Neo4j for path
        else:
            # First, see if there's a path to a preferred API call
            for api_pref in preferred:
                q =  "MATCH (n:NODE {{name: '{0}'}}) MATCH (m:NODE {{name: '{1}'}}) MATCH (p:NODE {{name: '{2}'}}) ".format(api1,api2,api_pref)
                q += "MATCH path=(n)-[:EDGE]->(p)-[:EDGE]->(m) "
                q += "RETURN 1"

                result_tmp = neo4j_db.query(q)
                if len(result_tmp) == 1:
                    result.append([[None,api_pref]])

            # If no preferred API paths were found, then see if there's different path
            if len(result) == 0:
                q =  "MATCH (n:NODE {{name: '{0}'}}) MATCH (m:NODE {{name: '{1}'}}) ".format(api1,api2)
                # Get path of exactly length 2
                q += "MATCH path=(n)-[:EDGE*2]->(m) "
                # LIMIT to return first "generations" number of results for speed
                q += "RETURN extract(node in nodes(path) | node.name) as nodes LIMIT {0}".format(generations)

                result = neo4j_db.query(q)

            # Cache result
            cache[key] = result

        # From result, extend paths
        # Randomly select result to force diversity
        for a in range(len(attack)):
            r = random.choice(result)
            api = r[0][1]

            # We put -1 in the PC place so we know that this is the call we inserted
            attack[a] += ';-1 {0}'.format(api)

    # Append final API call to attacks
    for a in range(len(attack)):
        attack[a] += ';{0}'.format(last)

    # Write final attack sequence(s) to folder
    for e,a in enumerate(attack):
        with open(os.path.join(attack_features,h,str(e)),'w') as fw:
            for api in a.split(';'):
                fw.write('{0}\n'.format(api))

def mimicry_wrapper(args):
    return mimicry(*args)
