FROM python:3.7
COPY . /asperathos-controller/
WORKDIR /asperathos-controller
RUN pip install setuptools tox flake8
ENTRYPOINT ./run.sh
