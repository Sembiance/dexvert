#!/bin/bash

for tableName in $(sqlite3 "$1" ".tables")
do
	sqlite3 "$1"<<- EXIT_HERE
	.mode csv
	.headers on
	.output "$2/$tableName.csv"
	SELECT * FROM $tableName;
	.exit
	EXIT_HERE
done