#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage "Checkout"
    checkout scm


    stage "Build base image"
    tryStep "build", {
        sh "docker-compose build"
    }

    stage 'Test'
    tryStep "Test", {
        sh "docker-compose -p panorama -f .jenkins/docker-compose.yml down"

        withCredentials([[$class: 'StringBinding', credentialsId: 'OBJECTSTORE_PASSWORD', variable: 'OBJECTSTORE_PASSWORD']]) {
            sh "docker-compose -p panorama -f .jenkins/docker-compose.yml build && " +
                    "docker-compose -p panorama -f .jenkins/docker-compose.yml run -u root --rm tests"
        }
    }, {
        step([$class: "JUnitResultArchiver", testResults: "reports/junit.xml"])

        sh "docker-compose -p panorama -f .jenkins/docker-compose.yml down"
    }

    stage "Build develop image"
    tryStep "build", {
        def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/panorama:${env.BUILD_NUMBER}", "web")
        image.push()
        image.push("develop")
    }
}

node {
    stage name: "Deploy to ACC", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-panorama.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                ]
    }
}


stage name: 'Waiting for approval'

input "Deploy to Production?"


node {
    stage 'Push production image'
    tryStep "image tagging", {
        def image = docker.image("admin.datapunt.amsterdam.nl:5000/datapunt/panorama:${env.BUILD_NUMBER}")
        image.pull()

        image.push("master")
        image.push("latest")
    }
}

node {
    stage name: "Deploy to PROD", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-panorama.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                ]
    }
}