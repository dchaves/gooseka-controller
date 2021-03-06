![Python](https://github.com/dchaves/gooseka-controller/workflows/Python/badge.svg)

## Introduction

Python controller for the solar powered car Gooseka

## Installation

Install dependencies with 

```
pip install -r requirements.txt
```


## Execution

To execute the controller you must specify a configuration file

```
python controller.py --config_file config/defaults.yaml
```

You can choose between different controllers by using the environment variable GOOSEKA. Current available options are:

* BENCHY: to test accelerations and decelerations
* RACE: to test the race controller
* any other value will use a gamepad as input
