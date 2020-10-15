# IRMA project

Inno Robot Module Application.

The web online service for remote managing a virtual robot. 

The key elements of the platform are Gazebo simulator and ROS Melodic framework.

The Gazebo consists of two parts:

1) Server - without GUI. Gazebo 9.0

2) Client - web client GzWeb. The source code for GzWeb is located at the osrf/gzweb Bitbucket repository.

https://bitbucket.org/osrf/gzweb

The simulator is started by ROS in a docker container. There is a Dockerfiles in gzweb-node directory.

Dockerfiles:

* **gzweb** - the image includes WEB client for gzserver
* **ros-melodic-gz-base** - It is a base image with gzserver and ros-core melodic
* **robo-node-ar601** - the image are built from ros-melodic-gz-base with code of a AR601
* **robo-node-yefan** - the image are built from ros-melodic-gz-base with code of a yefan

There are compose files to run containers:

* **ar-compose.yaml** - to run ar601 simulator
* **yefan-compose.yaml** - to run yefan simulator

![](http://cordelianew.university.innopolis.ru/gitea/robolab/IRMA/raw/branch/editor/img/irma.png)
### Building and deploying a docker container

1. Clone project:

	```bash	
	git clone ssh://git@cordelianew.university.innopolis.ru:2222/robolab/IRMA.git 
	````



2. Preparation

Build necessary images

example:

	```bash
	docker build -f gzweb -t gzweb:1.1 . 
	```

It needs to edit compose files according to your environment. 

3. RUN simulator

	```bash
	docker-compose -f ar-compose.yaml up -d
    ```


