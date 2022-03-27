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
pull-text:
	rm -rf thesis;
	git clone https://git.overleaf.com/61f1781dda616ff9b2082708 thesis;
	cd thesis && git push --mirror git@github.com:LukasForst/master-thesis.git;
	rm -rf thesis/.git;
	git add thesis;
	git commit -m "update thesis text" || exit 0;
	git push;

build-tex:
	(cd thesis && /Library/TeX/texbin/pdflatex main.tex);

install-latex-distro:
	brew install basictex;

install-tex-packages:
	tlmgr install algorithms algorithmicx biblatex;