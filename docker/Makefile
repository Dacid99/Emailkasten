image: build/Dockerfile build/docker-compose.build.yml entrypoint.sh
	sudo docker compose -f build/docker-compose.build.yml build

up: docker-compose.yml entrypoint.sh
	sudo docker compose up -d

down: docker-compose.yml entrypoint.sh
	sudo docker compose down

clean:
	sudo docker image rm emailkasten
