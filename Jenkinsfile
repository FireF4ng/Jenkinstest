pipeline {
    agent none
    stages {
        stage('Build and Analysis with SonarQube') {
            agent any
            steps {
                script {
                    // Exécution de la commande Maven pour construire et analyser avec SonarQube
                    sh 'mvn clean package sonar:sonar'
                }
            }
        }
    }
}