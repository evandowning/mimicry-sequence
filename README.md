# mimicry-sequence
Implements mimicry attack for sequence-based features

## Requirements
  * Debian 9 64-bit

## Clone repo
```
$ git clone git@github.com:evandowning/mimicry-sequence.git
```

## Install dependencies
```
$ ./setup.sh
```

## Configure Neo4j
```
# Set Neo4j database password
sudo -u neo4j neo4j-admin set-initial-password password
# Start Neo4j service
sudo service neo4j start
```

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
