#!/bin/bash
CODE_FILE=$1
g++ "/code/$CODE_FILE" -o /code/output
if [ -f "/code/input.txt" ]; then
    /code/output < /code/input.txt
else
    /code/output
fi
