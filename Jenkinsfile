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
            environment {
                scannerHome = tool 'sonar-scanner'
            }
            steps {
                echo 'Memindai keamanan algoritma Python...'
                
                withSonarQubeEnv('sonar-server'){
                    sh "${scannerHome}/bin/sonar-scanner \
                    -Dsonar.projectKey=skripsi-kripto-python \
                    -Dsonar.projectName='Skripsi Kriptografi Python' \
                    -Dsonar.sources=riset_kripto.py"
                }
            }
        }
        stage('3. Quality Gate Check') {
            steps {
                timeout(time : 10, unit: "MINUTES") {
                    echo 'Menunggu keputusan Quality Gate dari SonarQube...'
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('4. Build Docker Image') {
            steps {
                echo 'Membungkus algoritma menjadi Image Docker...'
                sh 'docker build -t aplikasi-kripto:latest .'
                echo 'Image Docker berhasil dirakit'
            }
        }
        stage('5. Push to Docker Hub') {
            steps {
                echo 'Mengunggah ke Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push spyustrrrrr/aplikasi-kripto:latest
                    '''
                }
            }
        }
    }
}