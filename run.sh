docker run -it -d --rm \
    -v $(pwd):/app \
    -p 5050:5050 \
    --name search \
    easysearch