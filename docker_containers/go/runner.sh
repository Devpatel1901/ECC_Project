#!/bin/bash
CODE_FILE=$1
if [ -f "/code/input.txt" ]; then
    go run "/code/$CODE_FILE" < /code/input.txt
else
    go run "/code/$CODE_FILE"
fi
