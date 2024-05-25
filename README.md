# Clojure project

This directory contains an implementation of the web shop application.

It contains the following files:
* web_shop.clj: an implementation of the service, encapsulating state in atoms and only using one thread.
* input_random.clj and input_simple.clj: two files with example inputs.
* run_benchmarks.sh: a script that runs the benchmarks and stores the results to files.
* clj, clj.bat, repl, repl.bat: helper scripts run your files, like seen in class.

To visualize benchmark results, we also provide a Python script that uses [matplotlib](https://matplotlib.org/):
* benchmarks/process_results.py: a Python script that parses benchmark results, calculates
  statistics, and generates plots.
* benchmarks/requirements.txt: a file listing the dependencies of the Python script, for use with pip.

To run the Python script, you first need to install the dependencies, preferably in a virtual environment:

```sh
$ cd benchmarks
# Create a new virtual environment in the folder venv:
$ python3 -m venv venv
# Activate the virtual environment in the current shell session:
$ source venv/bin/activate
# Install the dependencies:
$ python -m pip install -r requirements.txt
```

Every time you create a new terminal session, you'll need to activate the virtual environment first:

```sh
$ source venv/bin/activate
# You can now run:
$ python process_results.py
```

The script expects the benchmark results to be in files with names like `result-simple-1.txt`, in the benchmarks folder. The `run_benchmarks.sh` script puts them there.

You are free to modify all files as you wish. You do not need to use the provided Python code to visualize your benchmark results. These are merely provided to give you a starting point to automatically run and visualize benchmark results.
