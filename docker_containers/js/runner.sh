#!/bin/bash
CODE_FILE=$1
if [ -f "/code/input.txt" ]; then
    node "/code/$CODE_FILE" < /code/input.txt
else
    node "/code/$CODE_FILE"
fi
