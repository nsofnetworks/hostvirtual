@Library('jenkins-shared') _

pipeline {

    agent { label 'pfptprod-general' }

    options {
        ansiColor('xterm')
    }

    triggers {
        pollSCM('*/5 * * * *')
    }

    stages {
        stage('Build') {
            steps {
                build job: '/zubin/zubin-docker-base'
            }
        }
    }
    post {
        always {
            sendNotifications currentBuild.result
        }
    }
}
