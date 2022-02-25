# `clickup.py`

`clickup.py` is a neat script that automates the process of creating onboarding tasks
for new `rootski` contributors.

It's very easy to use (but you do need to be an "admin" in ClickUp).

## Invite new users to ClickUp

Tasks will be generated for any users added to our "People" section of our
ClickUp workspace. Here is a link to ours: https://app.clickup.com/18047884/settings/team/18047884/users

> 🗒 Note: you may need privileged access to see this page.

## Write a new task as a markdown file

You can write a new task description by adding a markdown file to
`rootski/infrastructure/clickup/onboarding-tasks`. The file name must end in `.md` (probably obvious).

The format of the markdown file should be like this:

```markdown
# <title>

## Project Context

A nice, detailed explanation of *what* the task entails and *why* it's necessary.

We can't include pictures, screenshots, or other assets because we're creating these
tasks programmatically (the ClickUp API may support that, we just haven't implemented
it yet if it does). But please include links to helpful resources like:

- tutorials
- snippets of our code in GitHub
- anything else helpful

Remember that the audience of onboarding tasks consists of people who may be *very* inexperienced
with software development, so remember write these a way that's accessible to beginners.

> 🗒 Note: you can do text with hyperlinks like this: [Eric's website](https://ericriddoch.info)

## Project Requirements

1. success criteria #1 (must be black/white so we know exactly when it's complete)
2. success criteria #2 (must be black/white so we know exactly when it's complete)
3. success criteria #3 (must be black/white so we know exactly when it's complete)
...
```

The text in the `<title>` will become the title of the task in ClickUp.

## Run the `clickup.py` script to generate that task for all users

```bash
cd rootski/infrastructure/clickup/

# create and activate a virtual environment
python -m venv ./venv/
source ./venv/bin/activate

# install the python libraries needed to run the script
make install

# go to the ClickUp UI and get an "API key" from
# ClickUp > Settings > My Apps > Apps > API Token.
# copy/paste that key into rootski/infrastructure/clickup/api-key.txt
# NEVER commit this! (this file is in .gitignore, so that's good)

# generate onboarding tasks for any new clickup users that aren't in users.json;
# if new *.md files have been added to ./onboarding-tasks/ since the last time
# the script was run, these new tasks will be generated to "backfill" these new
# ClickUp tasks for existing users
make generate-onboarding-tasks
```
