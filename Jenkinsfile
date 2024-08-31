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
            image: jenkins/agent:latest
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
        IMAGE_TAG = "v1.0.0-${BUILD_NUMBER}-${BUILD_DATE}"
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
                echo "Deploying to k8s cluster"
                  sh 'kubectl apply -f k8s/app-deployment.yaml'
                  sh 'kubectl apply -f k8s/app-service.yaml'
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

