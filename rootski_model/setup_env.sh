# export environment variables
__AWS__PROFILE__="rootski" # set this to the profile you want to use
export AWS_ACCESS_KEY_ID=$(aws configure get "${__AWS__PROFILE__}".aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get "${__AWS__PROFILE__}".aws_secret_access_key)
export AWS_DEFAULT_REGION="us-west-2"
