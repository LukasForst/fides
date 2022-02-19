install:
	conda env create --file conda.yml

update:
	conda env update --file conda.yml --prune