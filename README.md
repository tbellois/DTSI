# DTSI

This repository contains a Python application to verify all Docker images that are used in different public Github projects.  
The main program is located in the `dtsi.py` file.  
It is a program that returns json that contain every `FROM` Docker images with their version of every Dockerfile that can be found in a list of repository for a specified commit version.
It uses the Github API to :  
 * Get the git/trees of the specified version 
 * Get contents of every Dockerfile found in the Github project

## Install required dependencies

In order to start the application, it is necessary to install the required dependencies.  
To do this, you must execute the following command:

```console
$ pip install -r requirements.txt
...
```

## Inputs

`dtsi.py` needs a source URI that pointing to a plaintext file. Each line of this plaintext must have two fields separated by a space:
- the https url of the github public repository
- the commit SHA to verify

Github API have request restrictions rate if you are not authenticated. You can avoid it by using the token parameter. 

## Inputs parameter 

Parameters | Allowed value | Mandatory | Comment
-------|-------|-------|------
`-s` or `--source` | uri | X | uri that target the plaintext 
`-t` or `--token` | Valid Github access token  |  | Valid token to  to the Github API

## Input source

You must set a URI that point to a plaintext that contain a list of Github public repository.   
The content must be structure like this:

repo.git commit-sha

example value:
```
https://github.com/app-sre/qontract-reconcile.git 30af65af14a2dce962df923446afff24dd8f123e
https://github.com/app-sre/container-images.git c260deaf135fc0efaab365ea234a5b86b3ead404
...
```

## Personnal access token 

more informations [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

example value:
```
ghp_ppahsJmVuBABzwx8pt1sX7xRVw9eFR89DC7Q
```

## Output example

dtsi.py generate a json that follows this structure: 
```
{
  'data': {
    'https://github.com/app-sre/qontract-reconcile.git:30af65af14a2dce962df923446afff24dd8f123e': {
      'dockerfiles/Dockerfile': [
        'quay.io/app-sre/qontract-reconcile-base:0.2.1'
      ]
    }, 
    'https://github.com/app-sre/container-images.git:c260deaf135fc0efaab365ea234a5b86b3ead404': {
      'jiralert/Dockerfile': [
        'registry.access.redhat.com/ubi8/go-toolset:latest',
        'registry.access.redhat.com/ubi8-minimal:8.2'
      ], 
      'qontract-reconcile-base/Dockerfile': [
        'registry.access.redhat.com/ubi8/ubi:8.2', 
        'registry.access.redhat.com/ubi8/ubi:8.2', 
        'registry.access.redhat.com/ubi8/ubi:8.2'
      ]
    } 
  }
}
```