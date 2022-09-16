.. _database-page:

=========
Database
=========

This is the full data model of Rootski in an AWS DynamoDB table. Previously,
Rootksi was modeled using 15 Postgres tables and SQLAlchemcy, but recently we
decided to migrate our data to a single DynamoDB table using a "single table design".
We did this for the following reasons:

- Cost - Instead of Rootski costing $15 - $20 a month on AWS Lightsail, Rootski is essentially free with low traffic on DynamoDB.
- Database Latency - Given that DynamoDB is key-value store, our ability to read/write to Dynamo is much faster.
- Scalability - Dynamo was designed to easily scale and handle a large number of requests.

However, there are some draw backs.

- Adding new features - Creating a DynamoDB table requires us to make many assumptions about how our access patterns will be used. If that changes in the future, we may have to undo some of our assumptions and redesign the table.
- Joins - There are no joins in DynamoDB, so this makes performing some queries more difficult.
- No query Language - There is no official query language for DynamoDB.
- Duplicating Data - The data is duplicated making analytical queries difficult.

In order to use DynamoDB this required us to detail our access patterns before
modeling our data in a DynamoDB table. The image below is a table summarizing
the main access patterns in Rootski.

.. drawio-image:: ../../_static/infrastructure/dynamo-actions.drawio

Using these access patterns, we set up the following DynamoDB table with the following keys.

.. drawio-image:: ../../_static/infrastructure/dynamo-data-model.drawio


Here are the endpoints and queries we want to be able to run:

- `/breakdown/{word_id}` - The breakdown for the word associated with the user making the request
- `/breakdown` - Post a breakdown associated with the breakdown
- `/search/{search_term}` - Given a string of Roman OR Cyrillic characters (not both), what are all the words containing that substring?
- `/word/{word_id}/{word_type}` — Given a word ID, fetch the word data dictionary that includes things:
    - All the definitions and subdefinitions for that word
    - All of the example sentences for that word
    - The POS-dependent grammar information for the word: conjugations for verbs, declensions for adjectives and nouns, short forms for adjectives.
    - All the related words for that word (words that share the same *root*—not necessarily the same prefix or suffix)
