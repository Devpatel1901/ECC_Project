#!/bin/bash
set -e  # Exit on error

LANGUAGE=$1
CODE_FILE=$2

# Extract the file name without extension
FILE_NAME=$(basename "$CODE_FILE")
FILE_NAME_WITHOUT_EXTENSION="${FILE_NAME%.*}"

case $LANGUAGE in
    python)
        python3 "$CODE_FILE"
        ;;
    javascript)
        node "$CODE_FILE"
        ;;
    java)
        javac "$CODE_FILE"
        java -cp /app/code "$FILE_NAME_WITHOUT_EXTENSION"
        ;;
    cpp)
        g++ "$CODE_FILE" -o /app/a.out
        /app/a.out
        ;;
    go)
        go run "$CODE_FILE"
        ;;
    *)
        echo "Unsupported language!"
        exit 1
        ;;
esac
