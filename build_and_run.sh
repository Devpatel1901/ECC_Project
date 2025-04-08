#!/bin/bash

# build_and_run.sh - Build and run all language runner containers

set -e

# Define language-to-port mapping
languages=(
  "python|9001"
  "java|9002"
  "cpp|9003"
  "javascript|9004"
  "go|9005"
)

# Base path to Dockerfiles
BASE_PATH="./docker"

for index in "${!languages[@]}"; do

  pair="${languages[$index]}"
  lang="${pair%%|*}"
  port="${pair##*|}"

  echo $lang
  echo $port

  echo " Launching $container on port $port..."
  echo "    [debug] lang=$lang, port=$port"

  image="code-runner-$lang"
  container="runner-$lang"
  dockerfile_path="$BASE_PATH/$lang/Dockerfile"

  echo "\n Building Docker image for $lang..."
  docker build -t $image -f $dockerfile_path $BASE_PATH

  echo "Running container $container on port $port..."
  docker run -d --rm -i --name "$container" -p "$port":5000 "$image"

done

echo -e "\n All containers built and running."
echo "Test one with: curl -X POST http://localhost:9001/run -F 'file=@main.py' -F 'user_input=42'"