#!/bin/bash

# docker pull python:3.10-slim

(cd docker && docker compose -f compose.yml run --build  barometre_test "$@")

# For shell access, I'd want to do something like this:
#
# > (cd docker && docker run -ti barometre_test /bin/bash)
