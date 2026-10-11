stage('Deploy') {
    steps {
        sh '''
            cd /home/ubuntu/Event-booking-management
            git fetch origin main
            git reset --hard origin/main
            docker compose -p event-booking-management build
            docker compose -p event-booking-management up -d
        '''
    }
}
