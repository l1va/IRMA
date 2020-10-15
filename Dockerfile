FROM robolab.innopolis.university:5000/base-gzweb:latest

COPY gzweb-node/gzweb /home/gzweb

RUN cd /home/gzweb; ./deploy.sh -m local

COPY code_editor /home/code_editor
COPY start.sh start.sh
CMD ['./start.sh']
