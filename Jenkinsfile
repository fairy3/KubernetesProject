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
              sed -i 's|image: web-image:.*|image: web-image:${IMAGE_TAG}|g' k8s/web/web-deployment.yaml
              sed -i 's|image: python-app-image::.*|image:python-app-image:${IMAGE_TAG}|g' k8s/app/app-deployment.yaml
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
