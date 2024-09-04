@Library("my-shared-library") _
pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        metadata:
          namespace: jenkins
        spec:
          containers:
          - name: jenkins-agent
            image: mecodia/jenkins-kubectl:latest
            command:
            - cat
            tty: true
        '''
    }
  }

  options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        timestamps()
    }

    environment {
        APP_IMAGE_NAME = 'python-app-image'
        WEB_IMAGE_NAME = 'web-image'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        BUILD_DATE = new Date().format('yyyyMMdd-HHmmss')
    }

    stages {
        stage('Hello') {
           steps {
            wrap([$class: 'BuildUser']) {
              greet()
            }
           }
        }



      stage('Deploy to kubernetes') {
         steps {
             script {


              sh '''
                  echo "kubectl could not be found, installing..."
                  curl -LO "https://dl.k8s.io/release/v1.24.0/bin/linux/amd64/kubectl"
                  chmod +x ./kubectl

                  echo "Deploying to k8s cluster"
                  ./kubectl apply -f k8s/app-deployment.yaml
                  ./kubectl apply -f k8s/app-service.yaml
              '''
             }
         }
      }
    }

    post {
        always {
            // Clean up the workspace!
            cleanWs()
        }
        success {
            echo "Build ${BUILD_NUMBER} has succeeded"
        }
        failure {
            echo "Build ${BUILD_NUMBER} has failed"
        }
    }
}

