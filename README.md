# Fides

Global Trust Model for P2P Intrusion Prevention System (IDS/IPS). Named
after [Fides](https://en.wikipedia.org/wiki/Fides_(deity)) - goddess of trust and good faith. The repository is a mono
repo for my diploma thesis on CTU.

## Repository

* [files](fides) is the implementation of the trust model
* [simulations](simulations) are simulations used to evaluate the model
* [slips](slips) is the Slips module that uses Fides
* [tests](tests) are the unit tests that verify that Fides works
* [thesis](thesis) is my master's thesis that describes model and why was what implemented

## How to

Project needs to use same python as Slips does, thus we use Python 3.8, use [conda.yml](conda.yml) to setup project.
See [Makefile](Makefile) for setup.

## Configuration

See [fides.conf.yml](fides.conf.yml) that is used to parametrize trust model.

## Related work

* https://github.com/stratosphereips/StratosphereLinuxIPS
* https://github.com/stratosphereips/p2p4slips
* https://github.com/stratosphereips/p2p4slips-experiments
* https://github.com/stratosphereips/p2p4slips-tester
* https://github.com/draliii/StratosphereLinuxIPS/tree/module-p2p
