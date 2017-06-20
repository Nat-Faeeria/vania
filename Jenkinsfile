pipeline {
  agent any
  stages {
    stage('Dependencies') {
      steps {
        sh 'pip install .'
      }
    }
    stage('Build') {
      steps {
        sh 'python setup.py test'
      }
    }
  }
}