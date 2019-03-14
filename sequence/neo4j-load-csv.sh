#!/bin/bash

CYPHER_BIN="cypher-shell"
CYPHER_ARGS="-u $1 -p $2"

# Get list of CSV files
QUERY="\"
USING PERIODIC COMMIT 1000
LOAD CSV FROM 'file:///mimicry.csv' as line
MERGE (n1:NODE {name: line[0]})
MERGE (n2:NODE {name: line[1]})
CREATE UNIQUE (n1)-[:EDGE]->(n2)
\""

# Load CSV file into Neo4j
echo "${CYPHER_BIN}" "${CYPHER_ARGS}" "${QUERY}"
time eval "${CYPHER_BIN}" "${CYPHER_ARGS}" "${QUERY}"
