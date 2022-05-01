big01:
	bash -c 'conda activate fides && export PYTHONPATH="../../" && python big_parallel_01.py'

big02:
	bash -c 'conda activate fides && export PYTHONPATH="../../" && python big_parallel_02.py'

big02-b:
	rm nohup.out && nohup $(MAKE) big02 &