#!bin/bash

. /home/catkin_ws/devel/setup.bash
python3 /home/code_editor/manage.py runserver 0.0.0.0:$PORT_EDITOR\
& cd /home/gzweb/ && npm start

