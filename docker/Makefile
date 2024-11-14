image: Dockerfile entrypoint.sh
	sudo docker build -f Dockerfile -t emailkasten ..

up: docker-compose.yml Dockerfile entrypoint.sh
	sudo docker compose up --build &

down: docker-compose.yml Dockerfile entrypoint.sh
	sudo docker compose down

clean:
	sudo docker image remove emailkasten