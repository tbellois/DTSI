#!/usr/bin/python
# coding: utf-8

import sys
import argparse
import logging
import validators
import requests
import re
import json

NAME = 'DTSI'
EMAIL = 'thomas.bellois@gmail.com'
AUTHOR = 'Thomas Bellois'
VERSION = 'O.1.0'

"""
    Docker Trust Search Images
    Check Dockerfile from Docker images on Github public repository
    Take a url config file as input that contain 'url commit-sha' of every repository to check
"""


def initArgsParser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", help="target uri", required=True)
    parser.add_argument(
        "-t", "--token", help="Github Access   Token", required=False)
    return parser.parse_args(args)


def main():
    args = initArgsParser(sys.argv[1:])
    if args.source is not None:
        logging.info("Using uri: " + args.source)
        valid = validators.url(args.source)
        if valid != True:
            logging.error("Invalid uri")
            sys.exit(1)
        else:
            try:
                file = requests.get(args.source)
            except requests.exceptions.Timeout:
                sys.exit(1)
            except requests.exceptions.TooManyRedirects:
                sys.exit(1)
            if (file.status_code == 200):
                data = '{"data":{'  # Start Data Struct
                uri_input = file.text  # List of URI REF
                nb_repo = len(uri_input.split('\n'))  # NB_REPO to check
                for line in enumerate(uri_input.split('\n')):
                    nb_repo -= 1  # Remaining NB_REPO to check
                    if line[1].split():  # line not empty
                        uri = line[1].split(' ', 1)[0]  # first element
                        valid = validators.url(line[1].split(' ', 1)[0])
                        if valid != True:
                            logging.warning("Invalid git project " + uri)
                            continue
                        try:
                            ref = line[1].split(' ', 2)[1]  # second element
                        except IndexError:
                            logging.warning(
                                "Commit ref not found for uri " + uri)
                            continue
                        if len(ref) != 40:
                            logging.warning(
                                "Invalid sha1 commit for project " + uri)
                            continue
                        try:
                            # extract repo/owner references
                            repo_owner = re.search(
                                'https://github.com/(.+?).git', uri).group(1)
                            # ADD REPO:REF struct
                            data += '"'+line[1].replace(' ', ':')+'":{'
                        except AttributeError:
                            logging.warning("Bad repository URI for " + uri)
                            continue
                        if bool(args.token): #Test if Github Token is defined
                            response_tree = requests.get('https://api.github.com/repos/'+repo_owner+'/git/trees/'+ref, headers={
                                                         'Authorization': 'token '+args.token}, params={'recursive': '1'})
                        else:
                            response_tree = requests.get('https://api.github.com/repos/'+repo_owner+'/git/trees/'+ref, params={'recursive': '1'})
                        if response_tree.status_code == 403: # Error info for rate limit
                            logging.warning("You should set a Github Token")
                            response_tree.raise_for_status()
                        #print(response_tree.status_code)
                        if (response_tree.status_code != 200):  # Check if ressource exist
                            logging.warning(
                                "Reference not found " + uri + " with commit " + ref)
                            if nb_repo >= 1:
                                data += '},'  # NOT Last Repo
                            elif nb_repo == 0:
                                data += '}'  # Last Repo
                            continue
                        nb_path_found = len(response_tree.json()['tree'])
                        nb_dockerfile = 0  # init_nb_dockerfile_found
                        # List every path on repo
                        for path in response_tree.json()['tree']:
                            # Dockerfile Found
                            if path["path"].endswith("Dockerfile"):
                                nb_dockerfile += 1
                                if nb_dockerfile != 1:
                                    # ADD Dockerfile struct after another one
                                    data += ',"'+path["path"]+'":['
                                else:
                                    # ADD Dockerfile struct first one
                                    data += '"'+path["path"]+'":['
                                if bool(args.token): #Test if Github Token is defined
                                    response_file = requests.get('https://api.github.com/repos/'+repo_owner+'/contents/'+path["path"], headers={
                                                                 'Accept': 'application/vnd.github.VERSION.raw', 'Authorization': 'token '+args.token}, params={'ref': ref})
                                else:
                                    response_file = requests.get('https://api.github.com/repos/'+repo_owner+'/contents/'+path["path"], headers={
                                                                 'Accept': 'application/vnd.github.VERSION.raw'}, params={'ref': ref})

                                # Match * between FROM and space or return
                                images_version = re.findall(
                                    r'(FROM\s)(.*?)(?=\n|\s|\r|\\n)', str(response_file.content))
                                nb_images_found = len(images_version)
                                for tuple in images_version:  # List every images:ref
                                    data += '"'+tuple[1]+'"'
                                    if nb_images_found > 1:
                                        data += ','
                                    else:
                                        data += ']'
                                    nb_images_found -= 1
                            if nb_path_found == 1 and nb_repo >= 1:
                                data += '},'  # Last Dockerfile + NOT Last Repo
                            elif nb_path_found == 1 and nb_repo == 0:
                                data += '}'  # Last Dockerfile + Last Repo
                            nb_path_found -= 1
                data += '}}'  # Close Data Struct
                output = json.loads(data)
                print(output)


if __name__ == "__main__":
    main()
