pipeline {
  agent any
  stages {
    stage('Unit') {
      agent any
      steps {
        sh 'tox -e py27 -r'
      }
    }
    stage('Integration') {
      agent any
      steps {
        sh 'docker network create --attachable network-controller-$BUILD_ID'
        sh 'docker run -t -d --privileged --network=network-controller-$BUILD_ID -v /.kube:/.kube/ --name docker-controller-$BUILD_ID asperathos-docker'
        sh 'docker create --network=network-controller-$BUILD_ID --name integration-tests-controller-$BUILD_ID -e DOCKER_HOST=tcp://$(docker ps -aqf "name=docker-controller-$BUILD_ID"):2375 -e DOCKER_HOST_URL=$(docker ps -aqf "name=docker-controller-$BUILD_ID") integration-tests'
        sh 'docker cp . integration-tests-controller-$BUILD_ID:/integration-tests/test_env/controller/asperathos-controller/'
        sh 'docker start -i integration-tests-controller-$BUILD_ID'
      }
    }
  }
  post {
    cleanup {
      sh 'docker stop docker-controller-$BUILD_ID'
      sh 'docker rm -v docker-controller-$BUILD_ID'
      sh 'docker rm -v integration-tests-controller-$BUILD_ID'
      sh 'docker network rm network-controller-$BUILD_ID'
    }
  }
}
