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

pull-text:
	rm -rf thesis;
	git clone https://git.overleaf.com/61f1781dda616ff9b2082708 thesis;
	rm -rf thesis/.git;
	git add thesis;
	git commit -m "update thesis text";
	git push;
