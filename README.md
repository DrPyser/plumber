# Plumber
Multiplexed inter-process communication framework based on plan 9's [plumber](https://9fans.github.io/plan9port/man/man4/plumber.html).


The goal is to implement something like the plan 9 plumber system, in python, for unix/linux platforms.


## Modules

* communication protocols and formats
  * between user and plumber server
  * between plumber and handler programs
* rules specification
  * configuration
    * config file
	* dynamic(command interface)
  * matching
    * regex


## Concerns & design philosophy

* Modularity and extensibility. 
