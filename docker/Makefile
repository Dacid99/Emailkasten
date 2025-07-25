image: build/Dockerfile build/docker-compose.build.yml entrypoint.sh
	sudo docker build -f build/Dockerfile -t emailkasten:debug ../

migrations:
	sudo docker run --entrypoint "" --user 1000:1000 --rm -v ../:/mnt/ -w /mnt/ emailkasten poetry run python manage.py makemigrations

messages:
	sudo docker run --entrypoint "" --user 1000:1000 --rm -v ../:/mnt/ -w /mnt/ emailkasten poetry run python manage.py makemessages --all

up: docker-compose.yml entrypoint.sh
	sudo docker compose up -d

down: docker-compose.yml entrypoint.sh
	sudo docker compose down

clean:
	sudo docker image rm emailkasten
