@Library("my-shared-library") _

def autoCancelled = false

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
    GIT_CREDENTIALS_ID = 'github'
    DOCKERHUB_CREDENTIALS = 'dockerhub'
  }

  stages {
    stage('Hello') {
      steps {
        wrap([$class: 'BuildUser']) {
          greet()
        }
      }
    }

    stage('Check Commit') {
      steps {
        script {
          def commitMessage = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
          if (commitMessage.contains('[ci skip]')) {
            autoCancelled = true
            echo 'This is an automated commit. Skipping build.'
            currentBuild.result = 'SUCCESS'
          }
        }
      }
    }

    stage('Build Docker Image') {
      when {
        expression { !autoCancelled }
      }
      steps {
        container('docker') {
          sh '''
          /usr/local/bin/docker-compose -f ${DOCKER_COMPOSE_FILE} build
          '''
        }
      }
    }

    stage('Login to Docker Hub') {
    when {
        expression { !autoCancelled }
      }
      steps {
        container('docker') {
          withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
            sh '''
              echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
            '''
          }
        }
      }
    }

    stage('Tag and Push To DockerHub') {
    when {
        expression { !autoCancelled }
      }
      steps {
        container('docker') {
           script {
             def fullWebImageName = "${env.DOCKER_USERNAME}/${env.WEB_IMAGE_NAME}:${env.IMAGE_TAG}"
             def fullAppImageName = "${env.DOCKER_USERNAME}/${env.APP_IMAGE_NAME}:${env.IMAGE_TAG}"
             sh """
                docker tag ${WEB_IMAGE_NAME}:latest ${fullWebImageName}
                docker push ${fullWebImageName}

                docker tag ${APP_IMAGE_NAME}:latest ${fullAppImageName}
                docker push ${fullAppImageName}
            """
            }
            }
      }
    }

    stage('Update Manifests') {
      when {
        expression { !autoCancelled }
      }
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS_ID}", usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
            sh """
              git checkout main
              git config --global user.email "fairy3@gmail.com"
              git config --global user.name "fairy3"
              sed -i 's|image: rimap2610/web-image:.*|image: rimap2610/web-image:${IMAGE_TAG}|g' k8s/web/web-deployment.yaml
              sed -i 's|image: rimap2610/python-app-image:.*|image: rimap2610/python-app-image:${IMAGE_TAG}|g' k8s/app/app-deployment.yaml
              git add k8s/web/web-deployment.yaml
              git add k8s/app/app-deployment.yaml
              git commit -m "Update image to ${IMAGE_TAG} [ci skip]"
              git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/fairy3/KubernetesProject.git
            """
          }
        }
      }
    }
  }

  post {
    always {
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
