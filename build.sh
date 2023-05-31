docker stop $(docker ps -qa)
docker rm $(docker ps -qa)

docker build . -f Dockerfile.0 -t hgfkeep/translation:torch-1.9.0-cu102
docker build . -f Dockerfile.1 -t hgfkeep/translation:base
docker build . -t hgfkeep/translation:$(date +%m%d)

docker push hgfkeep/translation:torch-1.9.0-cu102
docker push hgfkeep/translation:base
docker push hgfkeep/translation:$(date +%m%d)