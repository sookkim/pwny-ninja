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
        withCredentials([[
          $class: 'AmazonWebServicesCredentialsBinding',
          credentialsId: 'sookyung-aws',
          accessKeyVariable: 'AWS_ACCESS_KEY_ID',
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
        ]]) {
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
        withCredentials([[
          $class: 'AmazonWebServicesCredentialsBinding',
          credentialsId: 'sookyung-aws',
          accessKeyVariable: 'AWS_ACCESS_KEY_ID',
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
        ]]) {
          sh '''
            set -eux
            export AWS_DEFAULT_REGION=ap-northeast-2

            # kubeconfig 보장
            aws eks update-kubeconfig --region ap-northeast-2 --name pwny-ninja --kubeconfig "$WORKSPACE/kubeconfig"

            # 리소스는 일단 apply (deployment/service 생성/유지 목적)
            kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n application apply -f k8s/service.yaml
            kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n application apply -f k8s/deployment.yaml

            # 여기서 이미지 태그를 커밋 SHA로 강제 변경 → 무조건 새 롤아웃 발생
            kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n application set image deploy/pwny-ninja \
              pwny-ninja=mikion279/pwny-ninja:${GIT_SHA}

            kubectl --kubeconfig "$WORKSPACE/kubeconfig" -n application rollout status deploy/pwny-ninja
          '''
        }
      }
    }
  }
}