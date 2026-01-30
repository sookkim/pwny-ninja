pipeline {
  agent any

  environment {
    IMAGE_NAME = "<REGISTRY>/pwny-ninja"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        script {
          env.GIT_SHA = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
          ).trim()
        }
      }
    }

    stage('Build Image') {
      steps {
        sh "docker build -t ${IMAGE_NAME}:${GIT_SHA} ."
      }
    }

    stage('Push Image') {
      steps {
        sh "docker push ${IMAGE_NAME}:${GIT_SHA}"
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        sh """
          sed -i 's|image:.*|image: ${IMAGE_NAME}:${GIT_SHA}|' k8s/deployment.yaml
          sed -i 's|value:.*|value: \"${GIT_SHA}\"|' k8s/deployment.yaml
          kubectl apply -f k8s/
        """
      }
    }

    stage('Smoke Check') {
      steps {
        sh "kubectl rollout status deployment/pwny-ninja"
      }
    }
  }
}