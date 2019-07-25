FROM stklik/scipy-notebook-z3

LABEL maintainer="Leo Goldstien <leo.goldstien@hcl.com>"

USER root

# install dependecies
RUN apt update 
RUN apt install libxtst6
USER $NB_USER
RUN pip install bitstring pyppeteer

# copy notebook
COPY z3_for_webapp_security.ipynb /home/jovyan
USER root
RUN chmod 777 /home/jovyan/z3_for_webapp_security.ipynb

USER $NB_USER
