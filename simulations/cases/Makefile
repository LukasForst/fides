.ONESHELL:

SHELL = /bin/bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate


big01:
	$(CONDA_ACTIVATE) fides && export PYTHONPATH="../../" && python big_parallel_01.py

big02:
	$(CONDA_ACTIVATE) fides && export PYTHONPATH="../../" && python big_parallel_02.py

big02-b:
	rm nohup.out && nohup $(MAKE) big02 &