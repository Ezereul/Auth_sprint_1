FROM ubuntu:latest
LABEL authors="ezereul"

ENTRYPOINT ["top", "-b"]