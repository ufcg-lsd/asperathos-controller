FROM python:2.7
COPY ./asperathos-controller/ /asperathos-controller/
WORKDIR /asperathos-controller
RUN pip install setuptools tox flake8
ENTRYPOINT ./run.sh
