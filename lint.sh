#!/bin/bash
set -o errexit

find stanity test -name '*.py' \
    | xargs pylint \
            --errors-only \
            --disable=print-statement

echo 'Passes pylint check'
