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

    stage('EKS Auth (kubeconfig)') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'aws-keys',
          usernameVariable: 'AWS_ACCESS_KEY_ID',
          passwordVariable: 'AWS_SECRET_ACCESS_KEY'
        )]) {
          sh '''
            set -eux
            export AWS_DEFAULT_REGION=ap-northeast-2

            aws sts get-caller-identity
            aws eks update-kubeconfig --region ap-northeast-2 --name pwny-ninja --kubeconfig "$WORKSPACE/kubeconfig"
            kubectl --kubeconfig "$WORKSPACE/kubeconfig" get nodes
          '''
        }
      }
    }

    stage('EKS Auth (kubeconfig)') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'sookyung-aws', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          sh '''
            set -eux
            export AWS_DEFAULT_REGION=ap-northeast-2

            aws sts get-caller-identity
            aws eks update-kubeconfig --region ap-northeast-2 --name pwny-ninja --kubeconfig "$WORKSPACE/kubeconfig"
            kubectl --kubeconfig "$WORKSPACE/kubeconfig" get nodes
          '''
        }
      }
    }


    stage('Debug kubectl context') {
  steps {
    sh '''
      set -eux
      whoami
      echo "HOME=$HOME"
      which kubectl || true
      kubectl version --client=true || true
      kubectl config current-context || true
      kubectl config view || true
    '''
  }
}

    stage('Deploy (kubectl apply)') {
      steps {
        sh """
          kubectl --kubeconfig "$WORKSPACE/kubeconfig" create namespace ${K8S_NAMESPACE} || true 

          mkdir -p /tmp/pwny-ninja
          cp -r k8s/* /tmp/pwny-ninja/

          sed -i.bak "s|DOCKERHUB_USER/pwny-ninja:REPLACE_TAG|${IMAGE_NAME}:${GIT_SHA}|g" /tmp/pwny-ninja/deployment.yaml
          sed -i.bak "s|value: \\"REPLACE_SHA\\"|value: \\"${GIT_SHA}\\"|g" /tmp/pwny-ninja/deployment.yaml

          kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n ${K8S_NAMESPACE} apply -f /tmp/pwny-ninja/
          kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n ${K8S_NAMESPACE} rollout status deploy/pwny-ninja
        """
      }
    }
  }
}