install:
	# production requirements
	pip install -e .

	# development requirements
	pip install rich boto3 pytest boto3-stubs[essential,cognito-idp] mypy moto[all] docker==5.0.3 python-jose==3.3.0

test:
	python -m pytest tests/test__custom_resource.py -xvs
