#!/usr/bin/env bash

# set -e makes the script exit if any command fails
# set -u makes the script exit if any unset variable is used
# set -o pipefail makes the script exit if any command in a pipeline fails
set -euo pipefail

for i in {1..30}
do
    echo "---"
    echo "> iteration $i"
    ./clj web_shop_parallel.clj > "benchmarks/result-random-$i.txt"
done

# echo "---  Random Input ---"
# for i in {1..30}
# do
#     echo "---"
#     echo "> iteration $i"
#     ./clj web_shop_parallel.clj > "benchmarks/results-random-$i.txt"
# done
