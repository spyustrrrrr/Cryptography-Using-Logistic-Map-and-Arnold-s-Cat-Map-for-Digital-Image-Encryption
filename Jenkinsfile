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
                sh 'docker build -t spyustrrrrr/aplikasi-kripto:latest .'
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
        post {
                success {
                    // Meminjam token rahasia SonarQube dari Jenkins
                    withSonarQubeEnv('sonar-server') {
                        sh """
                        # Menarik data menggunakan \$SONAR_AUTH_TOKEN sebagai izin masuk
                        STATS=\$(curl -s -u "\$SONAR_AUTH_TOKEN:" "\$SONAR_HOST_URL/api/measures/component?component=skripsi-kripto-python&metricKeys=bugs,vulnerabilities,code_smells")
                        
                        BUGS=\$(echo \$STATS | grep -o '"metric":"bugs","value":"[^"]*"' | cut -d'"' -f8)
                        VULN=\$(echo \$STATS | grep -o '"metric":"vulnerabilities","value":"[^"]*"' | cut -d'"' -f8)
                        SMELLS=\$(echo \$STATS | grep -o '"metric":"code_smells","value":"[^"]*"' | cut -d'"' -f8)

                        curl -s -X POST https://api.telegram.org/bot8936825066:AAHVFmEPqhjWmFWKgWNDLLVyqdFxmdPHqyI/sendMessage \\
                        -d chat_id=1383127210 \\
                        -d text="✅ Build #${BUILD_NUMBER} Sukses!
                        
        📊 LAPORAN SONARQUBE:
        - Bugs: \${BUGS:-0}
        - Kelemahan (Vuln): \${VULN:-0}
        - Code Smells: \${SMELLS:-0}

        Kapsul Python sudah siap di Docker Hub!"
                        """
                    }
                }
                failure {
                    withSonarQubeEnv('sonar-server') {
                        sh """
                        # Menarik data menggunakan \$SONAR_AUTH_TOKEN sebagai izin masuk
                        STATS=\$(curl -s -u "\$SONAR_AUTH_TOKEN:" "\$SONAR_HOST_URL/api/measures/component?component=skripsi-kripto-python&metricKeys=bugs,vulnerabilities,code_smells")
                        
                        BUGS=\$(echo \$STATS | grep -o '"metric":"bugs","value":"[^"]*"' | cut -d'"' -f8)
                        VULN=\$(echo \$STATS | grep -o '"metric":"vulnerabilities","value":"[^"]*"' | cut -d'"' -f8)
                        
                        curl -s -X POST https://api.telegram.org/bot8936825066:AAHVFmEPqhjWmFWKgWNDLLVyqdFxmdPHqyI/sendMessage \\
                        -d chat_id=1383127210 \\
                        -d text="❌ ALARM! Build #${BUILD_NUMBER} Gagal.
                        
        📊 KONDISI KODE SAAT INI:
        - Bugs: \${BUGS:-0}
        - Kelemahan (Vuln): \${VULN:-0}

        Segera cek baris kode mana yang rusak di:
        \${SONAR_HOST_URL}/dashboard?id=skripsi-kripto-python"
                        """
                    }
                }
            }
}