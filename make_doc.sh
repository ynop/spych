#!/usr/bin/env bash

cwd=$(pwd)

cd docs_sources

make html

cd $cwd

cp -R docs_sources/_build/html/. docs/