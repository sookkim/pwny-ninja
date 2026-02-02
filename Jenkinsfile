pipeline {
  agent any

  environment {
    DOCKERHUB_USER = "mikion279"
    IMAGE_NAME = "${DOCKERHUB_USER}/pwny-ninja"
    K8S_NAMESPACE = "application"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script {
          env.GIT_SHA = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
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
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh """
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${GIT_SHA}
          """
        }
      }
    }

    stage('Deploy (kubectl apply)') {
      steps {
        sh """
          kubectl create namespace ${K8S_NAMESPACE} || true

          mkdir -p /tmp/pwny-ninja
          cp -r k8s/* /tmp/pwny-ninja/

          sed -i.bak "s|DOCKERHUB_USER/pwny-ninja:REPLACE_TAG|${IMAGE_NAME}:${GIT_SHA}|g" /tmp/pwny-ninja/deployment.yaml
          sed -i.bak "s|value: \\"REPLACE_SHA\\"|value: \\"${GIT_SHA}\\"|g" /tmp/pwny-ninja/deployment.yaml

          kubectl -n ${K8S_NAMESPACE} apply -f /tmp/pwny-ninja/
          kubectl -n ${K8S_NAMESPACE} rollout status deploy/pwny-ninja
        """
      }
    }
  }
}