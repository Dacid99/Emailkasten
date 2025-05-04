image: build/Dockerfile build/docker-compose.build.yml entrypoint.sh
	sudo docker compose -f build/docker-compose.build.yml build

migrations:
	sudo docker run --entrypoint "" --rm -v $(pwd)/..:/mnt/ -w /mnt/ emailkasten poetry run python manage.py makemigrations

up: docker-compose.yml entrypoint.sh
	sudo docker compose up -d

down: docker-compose.yml entrypoint.sh
	sudo docker compose down

clean:
	sudo docker image rm emailkasten
