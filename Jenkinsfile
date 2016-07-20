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


String BRANCH = "${env.BRANCH_NAME}"
String INVENTORY = (BRANCH == "master" ? "production" : "acceptance")

node {
    stage "Checkout"
        checkout scm

    stage "Test"
    tryStep "Test",  {
            sh "docker-compose build"
            sh "docker-compose up -d"
            sh "sleep 20"
            sh "docker-compose up -d"
    }, {
            sh "docker-compose stop"
            sh "docker-compose rm -f"
        }

    stage "Build"
    tryStep "build", {
        def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/panorama:${BRANCH}", "web")
        image.push()

        if (BRANCH == "master") {
            image.push("latest")
        }
    }
}

node {
    stage name: "Deploy", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: INVENTORY],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-panorama.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: BRANCH],
                ]
    }
}
