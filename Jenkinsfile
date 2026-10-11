pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Validate') {
      steps { sh 'test -f backend/app.py && test -f frontend/package.json && test -f docker-compose.yml && test -f db/init.sql' }
    }
    stage('Build Docker images') { steps { sh 'docker compose build' } }
    stage('Deploy on main') {
      when { branch 'main' }
      steps { sh 'docker compose up -d' }
    }
  }
  post { always { sh 'docker compose ps || true' } }
}
