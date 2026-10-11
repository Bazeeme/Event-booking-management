pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE_PROJECT_NAME = 'event-booking-management'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    test -f backend/app.py
                    test -f frontend/package.json
                    test -f docker-compose.yml
                    test -f db/init.sql
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker compose -p "$COMPOSE_PROJECT_NAME" build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose -p "$COMPOSE_PROJECT_NAME" up -d'
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    docker compose -p "$COMPOSE_PROJECT_NAME" ps

                    for i in $(seq 1 20); do
                        if curl -fsS http://127.0.0.1/api/health; then
                            echo "Application health check passed"
                            exit 0
                        fi
                        sleep 3
                    done

                    docker compose -p "$COMPOSE_PROJECT_NAME" logs --tail=80
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose -p "$COMPOSE_PROJECT_NAME" ps || true'
        }
    }
}
