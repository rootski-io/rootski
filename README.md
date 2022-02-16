# Rootski

- [Rootski](#rootski)
- [Architecture Overview](#architecture-overview)
  - [Configuration Dependencies](#configuration-dependencies)
    - [Backend API (FastAPI)](#backend-api-fastapi)
    - [Frontend Website (React)](#frontend-website-react)
- [Deploying from Scratch](#deploying-from-scratch)
  - [1. Create the frontend S3 Bucket and Hosted Zone for `rootski.io`](#1-create-the-frontend-s3-bucket-and-hosted-zone-for-rootskiio)
  - [2. Bundle up the React project and sync those files with the S3 Bucket](#2-bundle-up-the-react-project-and-sync-those-files-with-the-s3-bucket)
  - [3. Create the EFS volume for persistent data files](#3-create-the-efs-volume-for-persistent-data-files)
  - [4. Create the EC2 Spot Instance Request for the backend](#4-create-the-ec2-spot-instance-request-for-the-backend)
  - [5. Populate the database files in the EFS volume](#5-populate-the-database-files-in-the-efs-volume)
- [Database Migrations](#database-migrations)
  - [Seeding the database from scratch](#seeding-the-database-from-scratch)

<br/>
<br/>
<br/>
<br/>

# Architecture Overview

The components of the Rootski architecture are:

1. **Frontend Static Website** --- An **S3 Bucket** set up to serve the **bundled React frontend** project as static files via a `HostedZone` for `rootski.io`.

2. **2 Subdomains** --- 2 **DNS Record Sets (A Records)** that point subdomains to the IP address of the backend EC2 Instance in **(3)**. The subdomains are:

   - `api.rootski.io`: **backend** the backend server
   - `traefik.rootski.io`: a dashboard that shows how and where `traefik` is routing requests (explained later)

   **Note**, the **A Records** have to be updated every time the IP address of the backend EC2 instance changes so that they point to the right place.

3. **Backend Webserver** --- A **spot instance request** for an **EC2 instance** that uses `docker swarm` to run:

   - [`FastAPI`](https://fastapi.tiangolo.com/) backend to serve responses to the frontend
   - `postgres` to serve all the Russian roots, words, sentences, etc. to the **backend**
   - [`traefik v2`](https://doc.traefik.io/traefik/) which is a proxy server / load balancer that:
     - forces `http` traffic to redirect to `https` at for traefik that has a `Host` HTTP request header of `api.rootski.io` or `traefik.rootski.io`
     - periodically acquires and renews TLS/SSL ACME certificates via LetsEncrypt so that the `https` traffic doesn't show up in the browser as "Insecure" and throw scary errors at the user. See [this funny comic](https://howhttps.works/) to learn what HTTPS really is and why these certificates are necessary. It gets 2 certs: 1 per Fully Qualified Domain Name (FQDN).

4. **Elastic File Service (EFS) Volume** --- A Network Attached Storage volume in AWS that **(3)** uses as a volume mount to store the postgres data files. Using this, the database files are able to persist, even though the files on the EC2 Spot Instance are permanently deleted every time it gets terminated.

5. **Cognito User Pool** --- Backend authentication service. It's set up with Google for login
and could also be set up with Facebook/Amazon/Apple. Once spun up,

  - the front end has a few variables in the `src/awd-cognito/auth-utils.tsx` file that need to be set so that the sign-in/sign-up/sign-out functionality points to that user pool.
  - the `rootski.auth.us-west-2.amazoncognito.com` URL may need to be added to the `rootski` app in a Google developer account to enable logging in with Google.

At the time of this writing, Cognito "Id Tokens" look like
this:

``` json
{
    "jwtToken": "eyJraWQiOiJ2QlU5akMxOFZZbWhCMDlVT0hWT0NoczlBMTV0XC84KzJUdkFKa1I2K2dqaz0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoieGFIeUxIZkZ6RDlsR1hZQVAwcjV6ZyIsInN1YiI6ImQwYzM5NzJjLTBiMGYtNDE3Ny04Y2ZiLTYzNmExNzMzMTUwNSIsImNvZ25pdG86Z3JvdXBzIjpbInVzLXdlc3QtMl9OTUFURmxjVkpfR29vZ2xlIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLXdlc3QtMi5hbWF6b25hd3MuY29tXC91cy13ZXN0LTJfTk1BVEZsY1ZKIiwiY29nbml0bzp1c2VybmFtZSI6Ikdvb2dsZV8xMTQxNjM0MDIyMTA5NjM3NzQxMzgiLCJvcmlnaW5fanRpIjoiNTlkNDE1YzAtNTQ0Ni00YzAyLTlkOTQtODU3Njk2MmIzZDQxIiwiYXVkIjoiMzV1ZmUxbmsydGFzdWcyZ21ibDVsOW1yYTMiLCJpZGVudGl0aWVzIjpbeyJ1c2VySWQiOiIxMTQxNjM0MDIyMTA5NjM3NzQxMzgiLCJwcm92aWRlck5hbWUiOiJHb29nbGUiLCJwcm92aWRlclR5cGUiOiJHb29nbGUiLCJpc3N1ZXIiOm51bGwsInByaW1hcnkiOiJ0cnVlIiwiZGF0ZUNyZWF0ZWQiOiIxNjI3MTgwNzUyMDkxIn1dLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTYyNzI0Nzg5MywiZXhwIjoxNjI3MjUxNDk5LCJpYXQiOjE2MjcyNDc4OTksImp0aSI6ImVlN2NkNGNlLTNiMTktNGNhNi05MzM3LTMzNTMzYmEyZmQ3YyIsImVtYWlsIjoiZXJpYy5yaWRkb2NoQGdtYWlsLmNvbSJ9.nJz4ShOABJawb0Iys9jakm0Lqbi0MAXDZWIsaeOi3fnw0PI5ScFzGs7RR3vruehJT02KAFYlTLtbT5jrEPdz67eB3xaTS190l_RAZ0zmO2zTDpu-RVaIa0I4D5F1KesfbHwkZ7X1985UzVW5ZRr9yz8hcPL06sTuvMneWNH_2GdR-xn7XFb8qLkPwKKtF5gH-oQvV0wIW4DdbJ06RMPiHDhv9KaeXRl2l74SZMq8plxpDTB2jii5_-7y-huXSE-oGt0qwgA0m_LzVkTjMa6vgqNoSOsqtnHXdO6b5Q4jCKxH1VD5VzjSrxQQYnFRGPIans7uPgMX1pIsDR8-12m45Q",
    "payload": {
        "at_hash": "xaHyLHfFzD9lGXYAP0r5zg",
        "sub": "d0c3972c-0b0f-4177-8cfb-636a17331505",
        "cognito:groups": [
            "us-west-2_NMATFlcVJ_Google"
        ],
        "email_verified": false,
        "iss": "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_NMATFlcVJ",
        "cognito:username": "Google_114163402210963774138",
        "origin_jti": "59d415c0-5446-4c02-9d94-8576962b3d41",
        "aud": "35ufe1nk2tasug2gmbl5l9mra3",
        "identities": [
            {
                "userId": "114163402210963774138",
                "providerName": "Google",
                "providerType": "Google",
                "issuer": null,
                "primary": "true",
                "dateCreated": "1627180752091"
            }
        ],
        "token_use": "id",
        "auth_time": 1627247893,
        "exp": 1627251499,
        "iat": 1627247899,
        "jti": "ee7cd4ce-3b19-4ca6-9337-33533ba2fd7c",
        "email": "eric.riddoch@gmail.com"
    }
}
```

The Rootski backend uses the email address as the user id so that if we ever delete the Cognito User Pool, users will still be able to access their account data from the Rootski database after signing
up again.

## Configuration Dependencies

### Backend API (FastAPI)

The FastAPI app has many items that need to be configured:

- The port to listen on
- any additional CORS URLs
- the URL of where to fetch the Cognito JWK keys used to decode/validate jwt tokens, this includes
  - The User Pool ID
  - The User Pool AWS Region

### Frontend Website (React)

The front end also has several variables that depend on AWS resources such as:

From CloudFormation

- User Pool ID
- User Pool Region
- Cognito Web Client ID
- Cognito redirect URLs (for logging in using the hosted UI)
- Cognito redirect URLs (for logging out using the hosted UI)

From Terraform

- The IP address of the backend Rootski API

<br/>
<br/>
<br/>
<br/>

# Deploying from Scratch

You will need the `AWS CLI` and `terraform` installed. The `terraform` files use the `[personal]` profile in `~/.aws/credentials`, so be sure to have that profile set up.

```bash
# install the aws cli
brew install awscli

# install the terraform CLI
brew install terraform
```

## 1. Create the frontend S3 Bucket and Hosted Zone for `rootski.io`

Run the `apply.sh` script in `infrastructure/cloudformation/front-end` to

- Create an S3 Bucket called `www.rootski.io`
- Create a Hosted Zone for `rootski.io` and point it at the S3 Bucket

This requires you to have the following ready in advance:

1. register the domain name `rootski.io` in Route53
2. create an AWS Certificate Manager for `www.rootski.io` and get the ARN

## 2. Bundle up the React project and sync those files with the S3 Bucket

In the directory `rootski_frontend/app` run

```bash
# deploy the react frontend to S3
npm run build && npm run deploy
```

- `npm run build` bundles the files and puts them in the `rootski_frontend/build/` folder
- `npm run deploy` syncs the `rootski_frontend/build/` folder with the `www.rootski.io` S3 bucket

You can see and configure these commands in `rootski_frontend/package.json` under `"scripts"`.

## 3. Create the EFS volume for persistent data files

First, in `infrasctucture/terraform/efs/main.tf`, comment out this block:

```hcl
terraform {
  backend "local" {
    path = "./.terraform/terraform.tfstate"
  }
}
```

This causes issues with the version of `.tfstate` files that terraform creates. As of the time this README was written, this block was present the last time `terraform apply` was run, so we are stuck with the current state file.

For a clean deployment of this architecture, that block should be removed.

In `infrastructure/terraform/efs`, run

```bash
terraform init
terraform apply
```

## 4. Create the EC2 Spot Instance Request for the backend

1. Find the EFS ID from the EFS volume created previously. This can be found in the `terraform.tfstate` file under the `efs/` terraform directory. It looks like this `fs-97ec6392`.

2. Place the EFS ID in `infrastructure/terraform/rootski-backend/variables.tf` and change the `efs_id` variable block by setting the `default` field as the current EFS ID like so:

```hcl
variable "efs_id" {
  type        = string
  default     = "fs-97ec6392"
  description = "Id of an EFS networked filesystem for the ec2 instance to mount and use. If empty string, an EFS will be created."
}
```

3. Create the spot request by running

```bash
terraform init
terraform apply
```

## 5. Populate the database files in the EFS volume

The vanilla dataset (with no user data) can be loaded from the `gather_data.py` script in another repo. Or you can run:

```bash
# copy all the local postgres datafiles to the efs volume
scp -i ~/.aws/eric-personal.pem -r  infrastructure/containers/postgres/* ec2-user@ip:/efs/rootski/ infrastructure/containers/postgres
```

<br/>
<br/>
<br/>
<br/>

# Database Migrations

This project uses [`alembic`](https://alembic.sqlalchemy.org/en/latest/tutorial.html) for handling database migrations for the
Postgres SQL database backend. See `rootski_api/migrations/` for the files related to database migrations.


## Seeding the database from scratch

The initial seed data for the rootski database comes from several
`.csv` files. These steps outline how to copy those files into the
`rootski_api` project, and load them into the database using alembic
migrations.

1. Check that the `rootski_api/migrations/initial_data/copy_initial_data_files.sh` script is configured correctly:

   - Check that the `DATA_MASTER_DIR` variable points to the
     `master/` data folder where the `.csv` files are located.
   - Add/remove files to the `DATA_FILES` array that will be used
     to seed the database.

2. Run the copy script to copy the base `.csv` data files from step 1 into the `migrations/initial_data/` directory

```bash
bash copy_initial_data_files.sh
```

3. In the `migrations/utils.py` script, add the connection string
   information for the environment you want to use.

4. Run the database migration to seed the data

```bash
# set this to the desired environment from utils.py
ROOTSKI_DB_ENVIRONMENT="local"

# the hash of the alembic revision which loads in the data files
ALEMBIC_REVISION="+1"

# run all the migrations up to and including the data seeding migration
pipenv install "path/to/pipfile/directory"
pipenv shell
$(pipenv --venv)/bin/alembic -x env="$ROOTSKI_DB_ENVIRONMENT" upgrade "$ALEMBIC_REVISION"
```


# Contributors

- [Isaac Robbins](https://www.linkedin.com/in/isaacrobbins/) - Learning and building experience in MLOps and DevOps!
