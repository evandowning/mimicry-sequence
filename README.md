# mimicry-sequence
Implements mimicry attack for sequence-based features

## Usage
```
# Load benign API sequences into Neo4j
$ cd sequence/
$ python create-neo4j-csv.py sequences/ classes.txt benign output.csv
$ cp output.csv /var/lib/neo4j/import/mimicry.csv
$ ./neo4j-load-csv.sh neo4j_username password
$ cd ../

# Run Mimicry attack
$ python mimicry.py mimicry.cfg
```
