# Z3 Demo Environment
This repository contains a Dockerfile to setup the environemnt used in """link to post""".

# Using the Repo
Requirements: git, docker
After cloning the repo, run:

  docker build -t z3_walkthrough .; docker run -it -p 8888:8888 z3_walkthrough
  
Note the output from this command, since it contains a line similar to this:

  http://(05640c9d300f or 127.0.0.1):8888/?token=e9a3e49b8fa92db5ba006c6a0c18d319bb361134cf1ab02f
  
Click the link or go to http://localhost:8888 and use the string after the '?toke=' to login to Jupyter.
