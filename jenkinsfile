pipeline {
  agent any
  environment {
    AWS_REGION = 'us-east-1'
    AWS_ACCOUNT_ID = '<aws_account_id>'
    APP_NAME = 'my-python-app'
    ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"
    BLUE_ENV = 'blue'
    GREEN_ENV = 'green'
  }
  stages {
    stage('Build') {
      steps {
        // Checkout source code from Git repository
        checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/AnupKrGhosh/assignment.git']]])
        
        // Build the Docker image
        sh "docker build -t ${ECR_REPO}:latest ."
      }
    }
    stage('Push to ECR') {
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: 'aws-creds', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]]) {
          // Login to ECR
          sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
          
          // Push the Docker image to ECR
          sh "docker push ${ECR_REPO}:latest"
        }
      }
    }
    stage('Deploy') {
      steps {
        // Create a new task definition
        sh "aws ecs register-task-definition --family ${APP_NAME} --container-definitions file://container-definition.json"
        
        // Create a new service with the blue environment
        sh "aws ecs create-service --service-name ${APP_NAME}-${BLUE_ENV} --task-definition ${APP_NAME}:1 --desired-count 1 --load-balancers targetGroupArn=<target_group_arn>,containerName=${APP_NAME},containerPort=80 --region ${AWS_REGION}"
        
        // Wait for the service to be fully deployed and healthy
        sh "aws ecs wait services-stable --cluster default --services ${APP_NAME}-${BLUE_ENV} --region ${AWS_REGION}"
        
        // Create a new service with the green environment
        sh "aws ecs create-service --service-name ${APP_NAME}-${GREEN_ENV} --task-definition ${APP_NAME}:1 --desired-count 0 --load-balancers targetGroupArn=<target_group_arn>,containerName=${APP_NAME},containerPort=80 --region ${AWS_REGION}"
      }
    }
    stage('Switch traffic to green environment') {
      steps {
        // Update the green environment desired count to 1 and blue environment desired count to 0
        sh "aws ecs update-service --service ${APP_NAME}-${GREEN_ENV} --desired-count 1 --region ${AWS_REGION}"
        sh "aws ecs update-service --service ${APP_NAME}-${BLUE_ENV} --desired-count 0 --region ${AWS_REGION}"
        
        // Wait for the green environment service to be fully deployed and healthy
        sh "aws ecs wait services-stable --cluster default --services ${APP_NAME}-${GREEN_ENV} --region ${AWS_REGION}"
      }
    }
    stage('Cleanup') {
      steps {
        // Delete the blue environment service
        sh "aws ecs delete-service --service ${APP_NAME}-${BLUE_ENV} --force --region ${AWS_REGION}"
      }
    }
  }
}
