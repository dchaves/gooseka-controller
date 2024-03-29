![Python](https://github.com/dchaves/gooseka-controller/workflows/Python/badge.svg)

## Introduction

Python controller for the solar powered car Gooseka

```
                 ┌────────────┐
                 │            │
                 │    STOP    │
   ┌─────────────►            ◄─────────────┐
   │             │            │             │
   │             │    ....    │             │
   │             └─────┬─▲────┘             │
   │                   │ │                  │
   │                 x │ │^                 │
   │                   │ │                  │
^  │             ┌─────▼─┴────┐             │ ^
   │             │            │             │
   │       o     │  STARTING  │     #       │
   │   ┌─────────┤            ├──────────┐  │
   │   │         │            │          │  │
   │   │   ┌─────►    ...    ◄──────┐   │  │
   │   │   │  x  └────────────┘   x  │   │  │
   │   │   │                         │   │  │
 ┌─┴───▼───┴──┐                   ┌──┴───▼──┴──┐
 │            │         #         │            │
 │  MAXPOWER  ├───────────────────►  LIMPING   │
 │            │                   │            │
 │            ◄───────────────────┤            │
 │    ...    │         o         │    ...    │
 └────────────┘                   └────────────┘
```

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
* AUTO: the race controller
* MACHOTE: directly using the controller, without software help
