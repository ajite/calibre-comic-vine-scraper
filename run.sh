#!/bin/sh
# Check if the container exists
if [ "$(docker ps -q -f name=calibrecli)" ]; then
  # If the container exists, stop and remove it
  docker stop calibrecli
  docker rm calibrecli
fi
docker run \
  -d\
  --name=calibrecli \
  -e PUID=1000 \
  -e PGID=100 \
  -e TZ=Asia/Shanghai \
  -v /volume1/Media/books:/config \
  -v /volume1/Code/calibre-comic-vine-scraper:/code\
  lscr.io/linuxserver/calibre:latest

docker exec -it calibrecli calibre-debug /code/update_calibre.py
docker stop calibrecli
docker rm calibrecli 
