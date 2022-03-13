# install python libraries needed to run the clickup.py script
# NOTE: before you run this, you should probably have a virtual environment
# created and activated first.
install:
	pip install -r requirements.txt

# reach out to ClickUp to see if there are any new users not present in
# users.json. Create an onboarding task and assign it to them for each
# .md file in clickup/onboarding-tasks/. If a new .md task template
# has been created, "backfill" this task for existing users.
generate-onboarding-tasks:
	python ./clickup.py
