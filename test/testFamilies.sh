#!/bin/bash

# Ordered from fastest to slowest
./testdexvert --skipBuild --format=poly
./testdexvert --skipBuild --format=executable
./testdexvert --skipBuild --format=font
./testdexvert --skipBuild --format=text
./testdexvert --skipBuild --format=other
./testdexvert --skipBuild --format=video
./testdexvert --skipBuild --format=document
./testdexvert --skipBuild --format=audio
./testdexvert --skipBuild --format=music
./testdexvert --skipBuild --format=image
./testdexvert --skipBuild --format=archive
