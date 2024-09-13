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
            image: docker:dind
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
                 container('jenkins-agent') {
                    // Build Docker image using docker-compose
                    sh '''
                    pwd
                    touch aaa
                    ls -l /usr/local/bin
                    sleep 3600
                    hostname
                    /usr/local/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} build
                    '''
                }
            }
        }

        stage('Snyk login') {
            steps {
                snykLogin('${SNYK_TOKEN}')
            }
        }

        stage('Snyk Container Test') {
            steps {
                script {
                    // Test Docker image for vulnerabilities
                    sh 'snyk container test ${APP_IMAGE_NAME}:latest --policy-path=.snyk'
               }
           }
       }        

       stage('Nexus login') {
            steps {
                nexusLogin("${NEXUS_CREDENTIALS_ID}","${NEXUS_PROTOCOL}","${NEXUS_URL}", "${NEXUS_REPOSITORY}")
            }
       }

      stage('Tag and Push To Nexus') {
             steps {
                script {
                sh '''
                    docker tag ${APP_IMAGE_NAME}:latest ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${WEB_IMAGE_NAME}:latest ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                 '''
                }
            }
      }

      stage('Install Kubernetes') {
        steps {
             script {

              sh '''
                  echo "kubectl could not be found, installing..."
                  curl -LO "https://dl.k8s.io/release/v1.24.0/bin/linux/amd64/kubectl"
                  chmod +x ./kubectl
              '''
             }
         }
      }

      stage('Update Manifests') {
            steps {
                script {
                    // Assuming you build a Docker image and tag it
                    def dockerImageTag = ${IMAGE_TAG}

                    // Update the Kubernetes manifests (e.g., deployment.yaml) with the new image tag
                    sh """
                    sed -i 's|image: app:.*|image: app:${dockerImageTag}|g' k8s/app-deployment.yaml
                    git add k8s/app-deployment.yaml
                    git commit -m "Update image to ${dockerImageTag}"
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

