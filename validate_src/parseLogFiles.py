# Script for parsing the standard error files generated by 
# Java and Python programs
import requests 
import os

# Open java log file and parse till the exception is detected
def parse_java_logs():
	print "[Started Parsing Java Logs]"
	currentJavaExceptions = []
	fjava = open("java_src/Testng/test.log","r")
	for line in fjava:
		if "Exception" in line:
			exception_query_string = line.split(":")[0].strip()
			
			if exception_query_string in currentJavaExceptions:
				continue
			else:
				currentJavaExceptions.append(exception_query_string)
				stackExItems = queryStackExchange(exception_query_string)
				createGitHubIssue(exception_query_string, stackExItems)
				createJiraIssue(exception_query_string, stackExItems)
	fjava.close()
	print "[Finished Parsing Java Logs]"

# Open Python log file and parse till the exception is detected
def parse_python_logs():
	print "[Started Parsing Python Logs]"
	fpython = open("python_src/python_program_log.log","r")
	for line in fpython:
		if "Error" in line:
			exception_query_string = line.strip()
			stackExItems = queryStackExchange(exception_query_string)
			createGitHubIssue(exception_query_string, stackExItems)
			createJiraIssue(exception_query_string, stackExItems)
	fpython.close()	
	print "[Finished Parsing Python Logs]"
			
# Query Stack Exchange API for the exception that has occured, and get top 4 responses matching it
def queryStackExchange(query):
	stackExItems = []
        url = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&q="+query.strip()+"&site=stackoverflow"
        with requests.Session() as session:
                json_response = session.get(url).json()
	stackExItems.append(json_response['items'][0]['link'])
	stackExItems.append(json_response['items'][1]['link'])
	stackExItems.append(json_response['items'][2]['link'])
	stackExItems.append(json_response['items'][3]['link'])
	return stackExItems	

# Create an issue in Github Repository with headless user
def createGitHubIssue(exception_query_string, stackExItems):
	print "[Started creating GitHub issue]"
	jenkins_build_number = os.environ.get('BUILD_NUMBER')
	jenkins_build_url = os.environ.get('BUILD_URL')
	curl_command = 'curl --user "jenkinslinkedin15:APGA2dPD" -i -d \'{"title": "Build '+jenkins_build_number+' Error: '+exception_query_string+'","body": "The Jenkins build failed with the exception marked in the title. \\nView the complete error log at: [Jenkins Build '+jenkins_build_number+']('+jenkins_build_url+')\\n\\nWe have the following possible solutions on Stack Exchange which match the Exception.\\n'+str(stackExItems[0])+'\\n'+str(stackExItems[1])+'\\n'+str(stackExItems[2])+'\\n'+str(stackExItems[3])+'\\n","labels": ["bug"]}\' https://api.github.com/repos/ashwintumma23/LinkedInHackDay/issues'
	os.system(curl_command)
	print "[Finished creating GitHub issue]"


# Create an issue in JIRA
def createJiraIssue(exception_query_string, stackExItems):
	print "[Starting creating JIRA issue]"
	jenkins_build_number = os.environ.get('BUILD_NUMBER')
	jenkins_build_url = os.environ.get('BUILD_URL')

	filecontents = ""
	jiraInputTemplate = open("validate_src/JiraInputTemplate.txt","r")
	for line in jiraInputTemplate:
		filecontents += line.strip()
	jiraInputTemplate.close()

	filecontents = filecontents.replace("__project__","LHD")	
	filecontents = filecontents.replace("__summary__","Build "+jenkins_build_number+" Error: "+exception_query_string)
	filecontents = filecontents.replace("__description__","The Jenkins build failed with the exception marked in the title.\\\\View the complete error log at:"+jenkins_build_url+"We have the following possible solutions on Stack Exchange which match the Exception.\n"+str(stackExItems[0])+"\n"+str(stackExItems[1])+"\n"+str(stackExItems[2])+"\n"+str(stackExItems[3])+"\n")	
	filecontents = filecontents.replace("__type__","Task")	

	jiraInput = open("validate_src/JiraInput.txt","w")
	jiraInput.write(filecontents)
	jiraInput.close()
	
	curl_command = 'curl -u admin:APGA2dPD -X POST -d @validate_src/JiraInput.txt https://linkedinhackday.atlassian.net/rest/api/2/issue --header "Content-Type:application/json"'
	os.system(curl_command)
	print "[Finished creating JIRA issue]"
	
def main():
	parse_java_logs()
	parse_python_logs()

main()
