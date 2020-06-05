#!/usr/bin/env bash

# docker command to start up a cpu version of the tensorflow serving model
docker run -it -p 9200:9200 --name crohns --network softwareengineering_group_project_CrohnsNetwork -v $(pwd)/serving_models/:/serving_models/ tensorflow/serving:latest --port=9200 --model_name=crohns --model_base_path=/serving_models/

# To stop: docker stop crohns && docker rm crohns
