#!/usr/bin/env python3
# This is a Python script that parses the benchmark results, calculates some
# statistics, and generates graphs. You can use it as a template and extend it
# as necessary. (You are not required to use this.)

# To get started, you need to create a Python virtual environment and install
# the dependencies, like this:
# $ python3 -m venv venv
# $ source venv/bin/activate
# $ pip install -r requirements.txt
#
# We use numpy [1] for statistics and matplotlib [2] for plotting.
#
# When running this script, make sure the virtual environment is activated!
# $ source venv/bin/activate
# $ python3 process_results.py
#
# [1] https://numpy.org/
# [2] https://matplotlib.org/

import logging
import glob
import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


# Name of the experiment.
EXPERIMENT_NAME = "inputs"
# Name of the benchmark. File names should be be result-$NAME-$ITERATION.txt.
BENCHMARK_NAME = r"result-(?P<name>.+)-(?P<iteration>\d+).txt"
# Expected benchmark names
NAMES = ["simple", "random_50_customers", "random_100_customers", "random_500_customers", "random_1000_customers", "random_2000_customers", "simple_2_threads", "simple_4_threads", "simple_8_threads", "random_50_customers_2_threads", "random_50_customers_4_threads", "random_50_customers_8_threads", "random_100_customers_2_threads", "random_100_customers_4_threads", "random_100_customers_8_threads", "random_500_customers_2_threads","random_500_customers_4_threads", "random_500_customers_8_threads", "random_1000_customers_2_threads", "random_1000_customers_4_threads", "random_1000_customers_8_threads", "random_2000_customers_2_threads", "random_2000_customers_4_threads", "random_2000_customers_8_threads",  "random_50_products_2_threads", "random_50_products_4_threads", "random_50_products_8_threads", "random_200_products_2_threads", "random_200_products_4_threads", "random_200_products_8_threads", "random_500_products_2_threads", "random_500_products_4_threads", "random_500_products_8_threads", "random_50_products", "random_200_products", "random_500_products"]

SEQUENTIAL = ["simple", "random_50_customers", "random_100_customers", "random_500_customers", "random_1000_customers", "random_2000_customers"]
PARALLEL = ["simple_2_threads", "simple_4_threads", "simple_8_threads", "random_50_customers_2_threads", "random_50_customers_4_threads", "random_50_customers_8_threads", "random_100_customers_2_threads", "random_100_customers_4_threads", "random_100_customers_8_threads", "random_500_customers_2_threads","random_500_customers_4_threads", "random_500_customers_8_threads", "random_1000_customers_2_threads", "random_1000_customers_4_threads", "random_1000_customers_8_threads", "random_2000_customers_2_threads", "random_2000_customers_4_threads", "random_2000_customers_8_threads"]

PARALLEL_50_CUSTOMERS = ["random_50_customers_2_threads", "random_50_customers_4_threads", "random_50_customers_8_threads"]
PARALLEL_100_CUSTOMERS = ["random_100_customers_2_threads", "random_100_customers_4_threads", "random_100_customers_8_threads"]
PARALLEL_500_CUSTOMERS = ["random_500_customers_2_threads", "random_500_customers_4_threads", "random_500_customers_8_threads"]
PARALLEL_1000_CUSTOMERS = ["random_1000_customers_2_threads", "random_1000_customers_4_threads", "random_1000_customers_8_threads"]

PARALLEL_2000_CUSTOMERS = ["random_2000_customers_2_threads", "random_2000_customers_4_threads", "random_2000_customers_8_threads"]

#benchmark comparison
SEQUENTIAL_VS_PARALLEL_SIMPLE = [ "simple", "simple_2_threads", "simple_4_threads", "simple_8_threads"] 

# customer load variation sequential vs parallel
SEQUENTIAL_VS_PARALLEL_RANDOM_50 = ["random_50_customers", "random_50_customers_2_threads", "random_50_customers_4_threads", "random_50_customers_8_threads"]
SEQUENTIAL_VS_PARALLEL_RANDOM_100 = ["random_100_customers", "random_100_customers_2_threads", "random_100_customers_4_threads", "random_100_customers_8_threads"]
SEQUENTIAL_VS_PARALLEL_RANDOM_500 = ["random_500_customers", "random_500_customers_2_threads", "random_500_customers_4_threads", "random_500_customers_8_threads"]
SEQUENTIAL_VS_PARALLEL_RANDOM_1000 = ["random_1000_customers", "random_1000_customers_2_threads", "random_1000_customers_4_threads", "random_1000_customers_8_threads"]
SEQUENTIAL_VS_PARALLEL_RANDOM_2000 = ["random_2000_customers", "random_2000_customers_2_threads", "random_2000_customers_4_threads", "random_2000_customers_8_threads"]

# customer load variation parallel only
PARALLEL_RANDOM_CUSTOMER_VARIATION = ["random_50_customers_8_threads", "random_100_customers_8_threads", "random_500_customers_8_threads","random_1000_customers_8_threads", "random_2000_customers_8_threads"]

PARALLEL_SEQUENTIAL_CUSTOMER_VARIATION = ["random_100_customers_4_threads", "random_100_customers","random_500_customers_4_threads", "random_500_customers","random_1000_customers_4_threads", "random_1000_customers", "random_2000_customers_4_threads", "random_2000_customers",]

RANDOM_SEQUENTIAL = ["random_50_customers", "random_100_customers", "random_500_customers", "random_1000_customers", "random_2000_customers"]
RANDOM_PARALLEL_BEST_CASE = ["random_50_customers_4_threads", "random_100_customers_4_threads", "random_500_customers_4_threads", "random_1000_customers_4_threads", "random_2000_customers_4_threads"]


# Varied number of products
RANDOM_VARIED_PRODUCTS_SEQUENTIAL = ["random_50_products", "random_200_products", "random_500_products"]
RANDOM_VARIED_PRODUCTS_PARALLEL = ["random_50_products_4_threads", "random_200_products_4_threads", "random_500_products_4_threads"]


names_key = {
    "sequential": SEQUENTIAL,
    "parallel": PARALLEL,
    "sequential_vs_parallel_simple": SEQUENTIAL_VS_PARALLEL_SIMPLE,
    "sequential_vs_parallel_random_50": SEQUENTIAL_VS_PARALLEL_RANDOM_50,
    "sequential_vs_parallel_random_100": SEQUENTIAL_VS_PARALLEL_RANDOM_100,
    "sequential_vs_parallel_random_1000": SEQUENTIAL_VS_PARALLEL_RANDOM_1000 
}


# Number of iterations expected per benchmark
NUMBER_OF_ITERATIONS = 30


# Set log level.
logging.basicConfig(level=logging.INFO)


def parse_file(filename: str, name: str) -> tuple[float, list[str]]:
    """Parses a benchmark result file and returns a tuple with a result
    and a list of parameters."""
    with open(filename) as f:
        contents = f.read()

    # The first 5 lines contain the parameters.
    lines = contents.split("\n")
    parameters = lines[:5]

    # The result is on a line that looks like "Elapsed time: 67.322677 msecs"
    # Note: this should only appear once in the file.
    pattern = r"\"Elapsed time: ([\d.]+) msecs\"\n"
    m = re.search(pattern, contents)
    if not m:
        raise Exception(f"Could not find result in file {filename}")
    time = float(m.group(1))

    return (time, parameters)


def parse_files(names: list[str]) -> dict[str, list[float]]:
    """Parse the benchmark files and return the results."""
    results = {name: [] for name in NAMES}
    parameters = {name: [] for name in NAMES}
    for filename in names:
        m = re.match(BENCHMARK_NAME, filename)
        if not m:
            continue
        name = m.group("name")
        if name not in NAMES:
            raise Exception(f"Unexpected benchmark name: {name}")
            
        result, pars = parse_file(filename, name)
        results[name].append(result)
        parameters[name].append(pars)
    # Check if parameters match across all files of the same benchmark.
    for name, pars in parameters.items():
        print(f"Params: {name} :: {pars}\n")
        for p in pars:
            if p != pars[0]:
                raise Exception(
                    f"Parameters do not match for all iterations of benchmark {name}:\n"
                    + f"{p} != {pars[0]}"
                )
        # logging.info(f"Parameters for {name}:\n%s", " - ".join(pars[0]))
    return results


def calculate_speedups(results: dict[int, list[float]]) -> dict[int, list[float]]:
    """Calculate the speedups for all results.

    The base time is the median of the results for 1 thread."""
    base = np.median(results[1])
    speedups = {i: [base / t for t in result] for (i, result) in results.items()}
    return speedups


def plot_boxplots(times: dict[str, list[float]], title):
    """Plot the results as boxplots."""
    mpl.rcParams.update({"font.size": 12})
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.subplots_adjust(bottom=0.275)    
    plt.xticks(rotation=22.5, ha="right")
    ax.boxplot([times[name] for name in times], notch=True, bootstrap=1000)
    # Note: the 'notch' represents the confidence interval, calculated using
    # bootstrapping, a statistical technique that resamples the data.
    # Note: matplotlib draws the whiskers at 1.5 * IQR from the 1st and 3rd quartile.
    # Points outside the whiskers are plotted as outliers (individual circles).
    # Different styles exist.
    # See https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.boxplot.html
    ax.set_title(title)
    ax.set_xlabel("Input file")
    ax.set_ylabel("Time (ms)")
    ax.set_xticks(list(range(1, len(times) + 1)))
    ax.set_xticklabels(list(times.keys()))
    ax.set_ylim(0, 1.1 * max([max(times[n]) for n in times]))
    fig.savefig(f"plots/result-{title}-boxplot.png")


def plot_violinplots(times: dict[str, list[float]], title):
    """Plot the results as violin plots (alternative)."""
    mpl.rcParams.update({"font.size": 12})
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.xticks(rotation=22.5, ha="right")
    plt.subplots_adjust(bottom=0.3)    
    ax.violinplot([times[name] for name in times], showmedians=True)
    # See https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.violinplot.html
    ax.set_title(title)
    ax.set_xlabel("Input file")
    ax.set_ylabel("Time (ms)")
    ax.set_xticks(list(range(1, len(times) + 1)))
    ax.set_xticklabels(list(times.keys()))
    ax.set_ylim(0, 1.1 * max([max(times[n]) for n in times]))
    fig.savefig(f"plots/result-{title}-violinplot.png")


def plot_errorbars(times: dict[str, list[float]], title):
    """Plot the results as plot with error bars."""
    mpl.rcParams.update({"font.size": 12})
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.xticks(rotation=90)

    x = list(times.keys())                  # ["random", "simple"]
    x_numbers = list(range(1, len(x) + 1))  # [1, 2]
    medians = [np.median(times[name]) for name in times]
    errors_down = [np.median(times[n]) - np.quantile(times[n], 0.25) for n in times]
    errors_up = [np.quantile(times[n], 0.75) - np.median(times[n]) for n in times]
    ax.errorbar(x_numbers, y=medians, yerr=[errors_down, errors_up], ls="none")
    ax.set_title(title)
    ax.set_xlabel("Input file")
    ax.set_ylabel("Time (ms)")
    ax.set_xticks(x_numbers)
    ax.set_xticklabels(x)
    ax.set_ylim(0, 1.1 * max([max(times[n]) for n in times]))
    fig.savefig(f"plots/result-{title}-errorbars.png")

def speedup(seq_times: dict[str, list[float]], par_times: dict[str, list[float]], map_key):
    plt.xticks(rotation=90)
    seq_paralel_map = map_key
    mean_seq = {key: np.mean(times) for key, times in seq_times.items()}
    mean_par = {key: np.mean(times) for key, times in par_times.items()}
    # x = list("50 customers", "100 customers", "500 customers", "1000 customers", "2000 customers")
    # speedup = {key: [t1 / t2 for t1, t2 in zip(seq_times[key], par_times[seq_paralel_map[key]])] for key in seq_times}
    mean_speedup = {key: mean_seq[key] / mean_par[seq_paralel_map[key]] for key in seq_times}

    keys = list(mean_speedup.keys())
    speedup_values = [mean_speedup[key] for key in keys]

    fig, ax = plt.subplots(figsize=(10, 6))
    plt.plot(keys, speedup_values, marker='o', linestyle='-', color='skyblue', label='Speedup')
    plt.xlabel('Number of Customers')
    plt.ylabel('Speedup')
    plt.title('Speedup when number of customers is increased')

    # Show grid
    plt.grid(True)

    # Show the plot
    # plt.show()
    fig.savefig(f"plots/result-speedup-number-of-customers.png")


def graph_results(input, title):
    time_quartiles = {
        i: np.quantile(input[i], [0.25, 0.5, 0.75]) for i in input
    }
    logging.info("Time quartiles for: %s", time_quartiles)
    plot_boxplots(input, title)

    # Alternative: plot using violin plots.
    plot_violinplots(input, title)

    # Alternative: plot using graph with error bars.
    plot_errorbars(input, title)


def main():
    # Gather benchmark files, i.e. all files in this directory that match the regex.
    files = glob.glob("result-*.txt")      

    # Parse benchmark results.
    results = parse_files(files)
    print(f"Res:: {results.keys()}")

    #simple seq vs parallel
    simple_sequential_parallel = {key: value for key, value in results.items() if key in SEQUENTIAL_VS_PARALLEL_SIMPLE}
    # graph_results(simple_sequential_parallel, "Simple Sequential vs Parallel Benchmark")

    # Sequential vs Parallel Random 50 customers
    random_50_sequential_parallel = {key: value for key, value in results.items() if key in SEQUENTIAL_VS_PARALLEL_RANDOM_50}
    # graph_results(random_50_sequential_parallel, "Random Sequential vs Parallel 50 customers Benchmark")

    # Sequential vs Parallel Random 100 customers
    random_100_sequential_parallel = {key: value for key, value in results.items() if key in SEQUENTIAL_VS_PARALLEL_RANDOM_100}
    # graph_results(random_100_sequential_parallel, "Random Sequential vs Parallel 100 customers Benchmark")

     # Sequential vs Parallel Random 500 customers
    random_100_sequential_parallel = {key: value for key, value in results.items() if key in SEQUENTIAL_VS_PARALLEL_RANDOM_500}
    # graph_results(random_100_sequential_parallel, "Random Sequential vs Parallel 500 customers Benchmark")

    # Sequential vs Parallel Random 1000 customers
    random_2000_sequential_parallel = {key: value for key, value in results.items() if key in SEQUENTIAL_VS_PARALLEL_RANDOM_2000}
    # graph_results(random_2000_sequential_parallel, "Random Sequential vs Parallel 2000 customers Benchmark")

    # varying number of customers.
    random_customer_variation = {key: value for key, value in results.items() if key in PARALLEL_RANDOM_CUSTOMER_VARIATION}
    # graph_results(random_customer_variation, "Varying customer load")

    parallel_sequential_customer_variation = {key: value for key, value in results.items() if key in PARALLEL_SEQUENTIAL_CUSTOMER_VARIATION}
    # graph_results(parallel_sequential_customer_variation, "Varying customer load comparsion")

    # Speedup calculation
    random_sequential = {key: value for key, value in results.items() if key in RANDOM_SEQUENTIAL}
    random_parallel_best_case = {key: value for key, value in results.items() if key in RANDOM_PARALLEL_BEST_CASE}
    map_to_use =  {
        "random_50_customers" : "random_50_customers_4_threads",
        "random_100_customers" : "random_100_customers_4_threads",
        "random_500_customers" : "random_500_customers_4_threads",
        "random_1000_customers" : "random_1000_customers_4_threads",
        "random_2000_customers" : "random_2000_customers_4_threads",
    }
    speedup(random_sequential, random_parallel_best_case, map_to_use)

    # product variation
    random_product_variation_parallel = {key: value for key, value in results.items() if key in RANDOM_VARIED_PRODUCTS_PARALLEL}
    graph_results(random_product_variation_parallel, "Varying products")



if __name__ == "__main__":
    main()
