#!/bin/bash
set -e  # Exit on error

LANGUAGE=$1
CODE_FILE=$2

# Extract the file name without extension
FILE_NAME=$(basename "$CODE_FILE")
FILE_NAME_WITHOUT_EXTENSION="${FILE_NAME%.*}"

case $LANGUAGE in
    python)
        pylint "$CODE_FILE"
        ;;
    javascript)
        eslint "$CODE_FILE"
        ;;
    java)
        java -jar /checkstyle.jar -c /google_checks.xml "$CODE_FILE"
        ;;
    cpp)
        cppcheck "$CODE_FILE"
        ;;
    go)
        golint "$CODE_FILE"
        go vet "$CODE_FILE"
        ;;
    *)
        echo "Unsupported language for static analysis!"
        exit 1
        ;;
esac
