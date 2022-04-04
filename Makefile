install:
	conda env create --file conda.yml

update:
	conda env update --file conda.yml --prune

redis:
	docker-compose up -d redis

redis-cli:
	docker exec -it fides-redis redis-cli

down:
	docker-compose down

test:
	pytest tests

## Latex Section
sync-text: update-text

update-text:
	rm -rf thesis;
	git clone https://git.overleaf.com/61f1781dda616ff9b2082708 thesis;
	cd thesis && git push --mirror git@github.com:LukasForst/master-thesis.git;
	rm -rf thesis/.git;
	git add thesis;
	git commit -m "sync thesis text" || exit 0;
	git push;

build-tex:
	# we do that twice to sync references
	(cd thesis && pdflatex main.tex && pdflatex main.tex);