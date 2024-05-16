# Challenge README:

## TL;DR
Prerequisites: Makefile and Go SDK (>1.17) (https://go.dev/doc/install)

``` 
  > source .env
  > make all
  > docker-compose up
```

## Functional requirements
- Build two services: one with a python client and other with a python server
- The server response has to include the domain and the client ip. Like an echo service.
- The client has to call the server on its 3 names using DNS resolution

## Non-functional requirements
- Generate a docker-compose with the two different services
- HTTPS will be used trusting the certificate (not skipping validation).
- Do not use any reverse proxy. 
- Share the project as “git bare” export, tar.gz compressed
- Secrets cannot be committed to the repo

## Folder Elements

```
.
└── challenge
    ├── harrow
    │   ├── harrow.py
    │   ├── Dockerfile
    │   ├── Makefile
    │   └── requirements.txt
    ├── compose.yaml
    ├── LICENSE.txt
    ├── Makefile
    ├── minica
    │   ├── go.mod
    │   └── main.go
    ├── README.md
    └── gideon
        ├── Dockerfile
        ├── Makefile
        ├── requirements.txt
        └── gideon.py
```
- Makefile: to build certificates, build and push images to repo
- compose.yaml: docker-compose manifest 
- **harrow** sub-folder contains:
  - the python code of the HTTPS client, 
  - the Makefile to build the docker image, 
  - and the Dockerfile of the docker image 
- **gideon** sub-folder contains: 
  - the python code of the HTTPS server,
  - the Makefile to build the docker image, 
  - and the Dockerfile of the docker image 
- **minica** sub-folder contains the go code to build the Certificate Generator (minica)

## Solution description

### gideon.py
Implements both an HTTP and HTTPS server.
The HTTPS server response is: 
```
Client connection from [client IP] to server [server name]
```
where, [client IP] is the IP address of the client and
[server name] is the server name used by the client, the TLS-SNI

The server also implements a HTTP (non secure) REST endpoint:
```
http://[server name]/root_ca
```
to provide the root_ca certificate to the client, so the client can trust the 
server certificate for secure connections.

### harrow.py
Implements the HTTP/HTTPS client. Obtain the root ca from the HTTP endpoint, and added it to the 
truststore. 
Run in a loop requesting the server using three different names (randomly). These names are:
- house1.[domain]
- house2.[domain]
...
- house9.[domain]

Docker Embedded DNS is used by the client.

### compose.yml
Describe the two services, both client and server, define the DNS entries (as links) 
to be added to the Docker embedded DNS, and inject the certificates as secrets to the server container.

### .env vars

| Name         | Description                          |
|--------------|--------------------------------------|
| MX_domain    | Domain name for certificates and DNS |
| MX_certspath | Path to create certificates          |

## Deployment of the solution

Prerequisites: Makefile and Go SDK (>1.17) (https://go.dev/doc/install)

1. Review and import env. vars from *.env* file
``` 
  > source .env
```
2. Build the certificates generator (minica) and images
``` 
  > make all
```
3. Launch the containers with docker-compose
``` 
  > docker-compose up
```

## Future Considerations
- CI/CD: Task related to build the certificates could be done by CI/CD engine as a previous task
- CI/CD: Define Build stage and Push images to repo
- GitOps: Use of K8S cluster to deploy the containers as Deployments, 
building the config repo in GIT to be pulled to trigger updates (rollout/rollback)
- Deployment: For productive environments, use of CA signed certificates


### Thanks to
Minica, the Certificates Generator at https://github.com/jsha/minica and Tamsyn Muir, for her books about The Locker Tomb
