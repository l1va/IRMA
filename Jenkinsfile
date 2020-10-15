#!groovy
pipeline{
	agent none
	stages{
		stage('Test'){
			agent{
				docker{
					label 'agent-1'
					image 'base-gzweb:latest'
					registryUrl 'https://robolab.innopolis.university:5000'
					registryCredentialsId 'jenkins-service'
					args '-u 0:0'
				}
			}
			steps{

					sh "/bin/bash -c './gzweb-node/gzweb/deploy.sh -m local'"
					sh "uname -a"
					echo "TEST SUCCESS!"
						
			}
		}
		stage('Build'){
			agent{ 
				label 'agent-1'
			}
			environment{
				registry = 'robolab.innopolis.university:5000/gzweb-node'
				tag_beta ='latest'
			}
			steps{
				script{
					def dockerfile = 'Dockerfile'
					def image = docker.build("${env.registry}:${env.tag_beta}", "-f ${dockerfile} ./")
					withDockerRegistry([credentialsId: "jenkins-service", url: "https://robolab.innopolis.university:5000"]){
						image.push()
					}
				}
			}
		}
	}
}
