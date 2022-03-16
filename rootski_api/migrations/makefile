# install python dependencies needed to run the database migrations
install:
	python -m pip install -e .

# generate a new database revision file
new-revision:
	@echo "[rootski] Please enter a SHORT name for the revision (spaces will be replaced with underscores): "; \
    read REVISION_NAME; \
    echo "Creating a migration file with name: $$REVISION_NAME" \
	\
	&& alembic revision \
		-m "$$REVISION_NAME" \
		--rev-id $$(python -m migrations.utils.get_new_revision_id)
