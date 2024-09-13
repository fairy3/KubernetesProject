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
          - name: docker
            image: docker:latest
            command:
            - cat
            tty: true
            volumeMounts:
             - mountPath: /var/run/docker.sock
               name: docker-sock
          volumes:
          - name: docker-sock
            hostPath:
              path: /var/run/docker.sock
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
        IMAGE_TAG = "v1.0-${BUILD_NUMBER}-${BUILD_DATE}"
        SNYK_TOKEN = credentials('snyk-token')
        NEXUS_PROTOCOL = "http"
        NEXUS_URL = "172.24.216.163:8888"
        NEXUS_REPOSITORY = "my-docker-repo"
        NEXUS_CREDENTIALS_ID = "nexus"
    }

    stages {
        stage('Hello') {
           steps {
            wrap([$class: 'BuildUser']) {
              greet()
            }
           }
        }

        stage('Build Docker Image') {
            steps {
                 container ('docker') {
                    // Build Docker image using docker-compose
                    sh '''
                    /usr/local/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} build
                    '''
                }
            }
        }

      // stage('Nexus login') {
      //      steps {
      //          container ('docker') {
      //              nexusLogin("${NEXUS_CREDENTIALS_ID}","${NEXUS_PROTOCOL}","${NEXUS_URL}", "${NEXUS_REPOSITORY}")
      //          }
      //      }
      // }

      stage('Tag and Push To Nexus') {
         steps {
            container ('docker') {
                sh '''
                    docker tag ${APP_IMAGE_NAME}:latest ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                    #docker push ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${WEB_IMAGE_NAME}:latest ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                    #docker push ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                 '''
            }
        }
      }

      //stage('Install Kubernetes') {
      //  steps {
      //       container ('docker') {
//
      //        sh '''
      //            echo "kubectl could not be found, installing..."
      //            curl -LO "https://dl.k8s.io/release/v1.24.0/bin/linux/amd64/kubectl"
      //            chmod +x ./kubectl
      //        '''
      //       }
      //   }
      //}

      stage('Update Manifests') {
            steps {
                script {
                    // Assuming you build a Docker image and tag it
                    //def dockerImageTag = ${IMAGE_TAG}

                    // Update the Kubernetes manifests (e.g., deployment.yaml) with the new image tag
                    sh """
                    sed -i 's|image: app:.*|image: app:${IMAGE_TAG}|g' k8s/app-deployment.yaml
                    git add k8s/app-deployment.yaml
                    git commit -m "Update image to ${IMAGE_TAG}"
                    git push origin main
                    """
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

