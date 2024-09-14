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
        NEXUS_PROTOCOL = "http"
        NEXUS_URL = "172.24.216.163:8888"
        NEXUS_REPOSITORY = "my-docker-repo"
        NEXUS_CREDENTIALS_ID = "nexus"
        GIT_CREDENTIALS_ID = 'github'
        SKIP_BUILD = ''
    }

    stages {
        stage('Hello') {
           steps {
            wrap([$class: 'BuildUser']) {
              greet()
            }
           }
        }

        stage('Initialize') {
      steps {
        script {
          // Initialize Groovy variables
          env.SKIP_BUILD = ''
        }
      }
    }
         stage('Check Commit') {
             steps {
                script {
                     def commitMessage = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                     if (commitMessage.contains('[ci skip]')) {
                        echo 'This is an automated commit. Skipping build.'

                        // Set environment variable to indicate skipping the build
                        env.SKIP_BUILD = 'true'
                     }
                }
            }
         }

         stage('Build Docker Image') {
      steps {
        script {
          if (env.SKIP_BUILD != 'true') {
            container('docker') {
              // Build Docker image using docker-compose
              sh '''
              /usr/local/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} build
              '''
            }
          } else {
            echo 'Skipping Build Docker Image stage due to [ci skip].'
          }
        }
      }
    }

       stage('Update Manifests') {
      steps {
        script {
          if (env.SKIP_BUILD != 'true') {
            // Update the Kubernetes manifests (e.g., deployment.yaml) with the new image tag
            withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
              sh """
                git checkout main
                git config --global user.email "fairy3@gmail.com"
                git config --global user.name "fairy3"
                sed -i 's|image: rimap2610/web-image:.*|image: rimap2610/web-image:${IMAGE_TAG}|g' k8s/web-deployment.yaml
                git add k8s/web-deployment.yaml
                git commit -m "Update image to ${IMAGE_TAG} [ci skip]"
                git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/fairy3/KubernetesProject.git
              """
            }
          } else {
            echo 'Skipping Update Manifests stage due to [ci skip].'
          }
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

