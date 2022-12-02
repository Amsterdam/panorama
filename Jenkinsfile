#!groovy

String PLAYBOOK = 'deploy.yml'

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node {
    stage("Checkout") {
        checkout scm
        withCredentials([[$class: 'StringBinding', credentialsId: 'GOOGLE_APP_CREDENTIALS', variable: 'APP_CREDENTIALS']]) {
            writeFile file: "web/panorama/google-application-credentials.json", text: "${APP_CREDENTIALS}"
        }
    }

    stage('Test') {
        tryStep "test", {
            sh "docker-compose -p panorama -f web/deploy/test/docker-compose.yml down"
            withCredentials([
                [$class: 'StringBinding', credentialsId: 'panorama_objectstore_user', variable: 'OBJECTSTORE_PASSWORD'],
                [$class: 'StringBinding', credentialsId: 'panorama_objectstore_key', variable: 'OBJECTSTORE_USER'],
                [$class: 'StringBinding', credentialsId: 'panorama_panorama_tenant_id', variable: 'PANORAMA_TENANT_ID'],
                [$class: 'StringBinding', credentialsId: 'panorama_datapunt_tenant_id', variable: 'DATAPUNT_TENANT_ID']
            ]) {
                sh "docker-compose -p panorama -f web/deploy/test/docker-compose.yml build && " +
                   "docker-compose -p panorama -f web/deploy/test/docker-compose.yml run -u root --rm tests"
            }
        }, {
            sh "docker-compose -p panorama -f web/deploy/test/docker-compose.yml down"
        }
    }

    stage("Build image") {
        tryStep "build", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                def image = docker.build("datapunt/panorama:${env.BUILD_NUMBER}", "web")
                image.push()
            }
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.image("datapunt/panorama:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: "${PLAYBOOK}"],
                    [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_panorama"],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'Panorama is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.image("datapunt/panorama:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("production")
                    image.push("latest")
                }
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: "${PLAYBOOK}"],
                    [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_panorama"],
                ]
            }
        }
    }
}
