#!/bin/bash
CODE_FILE=$1
if [ -f "/code/input.txt" ]; then
    python3 "/code/$CODE_FILE" < /code/input.txt
else
    python3 "/code/$CODE_FILE"
fi
