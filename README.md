# Happyfox_assignment

Step 1:
Configure Google console for getting credentials.json file for "OAuth 2.0 Client IDs"

1a. Define scope while configuring otherwise an error will occur while executing script "You are not authorized to access this for client Id *****".
1b. Define test users/ allowed users also

After this credentials will generate and we can download credentials.json from there.

Step2: 

enable api using below link:
https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=2036113391

Step3:

Create virtual env:
python3 -m venv test_env

Activate virutal env:
pip3 install virtualenv
virtualenv test_env
. test_env/bin/activate

Install pip3:
sudo apt install python3-pip

Install google client using pip:
pip3 install google-api-python-client

Install google oauth client using pip:
pip3 install oauth2client
sudo pip3 install google-auth-oauthlib
pip3 install google-auth-oauthlib

Install sqlite:
sudo apt install sqlite3 

Check sqlite version:
sqlite3 --version

Query for manually creating a table:
CREATE TABLE IF NOT EXISTS test(id TEXT PRIMARY KEY, sample TEXT);

Connect with sqlite from cmd:
sqlite3 emails.db

Show tables:
.tables


Generate Token:
authenticate function will generate token and create a file in folder, after token is expired, we need to generate it again by deleting previous file.
Error when token is expired: "Authorized user info was not in the expected format, missing fields refresh_token."
Note: We have different scope for both scripts. For executing rules, I have used modify scope.

File for authentication, fetching emails and storing:
assignment.py

File for executing rule:
execute_rules.py


Assumptions:
We are handling input format against each filter we are applying. For example, "Date Received" will never contain a string value. This means, if there is "contains" in filter it will never be against "Date Received".

Note:
I have used personal email for this because of this reason not adding credentials.json in git 
