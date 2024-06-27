#!/usr/bin/env bash

# set -e makes the script exit if any command fails
# set -u makes the script exit if any unset variable is used
# set -o pipefail makes the script exit if any command in a pipeline fails
set -euo pipefail

for i in {1..30}
do
    echo "---"
    echo "> iteration $i"
    ./clj web_shop_parallel.clj > "benchmarks/result-random_500_products_4_threads-$i.txt"
    # ./clj web_shop.clj > "benchmarks/result-random_50_products-$i.txt"
done
# In the benchmarking I changed the file name to match with the bechmark being run

