
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        PROJECT_NAME = 'event-booking-management'
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/Bazeeme/Event-booking-management.git'

                echo 'GitHub checkout completed.'
            }
        }

        stage('Validate Configuration') {
            steps {
                sh '''
                    set -eu

                    test -f "$COMPOSE_FILE"
                    test -f backend/Dockerfile
                    test -f frontend/Dockerfile

                    docker --version
                    docker compose version

                    echo "Configuration validation successful."
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    set -eu

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        -p "$PROJECT_NAME" \
                        build
                '''
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                sh '''
                    set -eu

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        -p "$PROJECT_NAME" \
                        up -d --remove-orphans

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        -p "$PROJECT_NAME" \
                        ps

                    echo "Deployment commands completed."
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Event Booking deployment completed.'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
