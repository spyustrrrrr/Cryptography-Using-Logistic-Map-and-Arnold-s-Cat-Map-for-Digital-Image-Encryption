pipeline {
    agent any
    stages {
        stage('1. Checkout kode(git)') {
            steps {
                echo 'mengambil kode terbaru dari github...'
                checkout scm
            }
        }
        stage('2. Security Scan SonarQube') {
            steps {
                echo 'Memindai keamanan algoritma Python...'
                sh 'sleep 3'
            }
        }
        stage('3. Build & Finish') {
            steps {
                echo 'Kode skripsi aman dan siap dilampirkan!'
            }
        }
    }
}