#!groovy

node {

    String BRANCH = "${env.BRANCH_NAME}"
    
    if (BRANCH == "master") {
        INVENTORY = "production"
    } else {
        INVENTORY = "acceptance"
    }
    echo "Branch is ${BRANCH}"
    echo "Inventory is ${INVENTORY}"


    stage "Checkout"
        checkout scm

    stage "Test"

        try {
            sh "docker-compose build"
            sh "docker-compose up -d"
            sh "sleep 20"
            sh "docker-compose up -d"

        }
        finally {
            sh "docker-compose stop"
            sh "docker-compose rm -f"
        }


    stage "Build"

        def image = docker.build("admin.datapunt.amsterdam.nl:5000/datapunt/panorama:${BRANCH}", "web")
        image.push()

        if (BRANCH == "master") {
            image.push("latest")
        }

    stage "Deploy"

        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: INVENTORY],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-panorama.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: BRANCH],
                ]
}