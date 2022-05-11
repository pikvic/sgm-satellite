# base image
FROM ubuntu

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
#RUN add-apt-repository ppa:ubuntugis/ppa
RUN apt-get update
RUN apt-get install python3 python3-pip build-essential libssl-dev libffi-dev python3-dev gdal-bin libgdal-dev python3-rasterio -y
RUN pip install -r requirements.txt
RUN pip install pyproj aiofiles
# copy project
COPY . /usr/src/app