#!/bin/sh
NEW_PATH=$(echo $1 | sed 's/\/volume1\/Downloads\//\/downloads\//')
docker exec -it calibre calibredb --with-library="/books/" add "$NEW_PATH"
