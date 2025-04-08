#!/bin/bash
CODE_FILE=$1
CLASS_NAME=$(basename "$CODE_FILE" .java)
javac "/code/$CODE_FILE"
if [ -f "/code/input.txt" ]; then
    java -cp /code "$CLASS_NAME" < /code/input.txt
else
    java -cp /code "$CLASS_NAME"
fi
