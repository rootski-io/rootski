.. _database-page:

.. |secure| raw:: html

   <i class="fa-solid fa-lock" style="color: #03a9f4"></i>

.. |dollar| raw:: html

   <i class="fa-solid fa-dollar" style="color: #03a9f4"></i>

.. |users| raw:: html

   <i class="fa-solid fa-users" style="color: #03a9f4"></i>

.. |ghost| raw:: html

   <i class="fa-solid fa-ghost" style="color: #03a9f4"></i>

.. |flag| raw:: html

   <i class="fa-solid fa-flag" style="color: #03a9f4"></i>

.. |timer| raw:: html

   <i class="fa-solid fa-clock" style="color: #03a9f4"></i>

.. |cloud| raw:: html

   <i class="fa-solid fa-cloud" style="color: #03a9f4"></i>

=========
Database
=========

This is the full data model of Rootski in an AWS DynamoDB table. Previously,
Rootksi was modeled using 15 Postgres tables and SQLAlchemcy, but recently we
decided to migrate our data to a single DynamoDB table using a "single table design".
We did this for the following reasons:

Benefits of DynamoDB over SQL
-------------------------------

- |dollar| **Cost**: Instead of Rootski costing $15 - $20 a month on AWS Lightsail, Rootski is essentially free with low traffic on DynamoDB.
- |timer| **Database Latency**: Given that DynamoDB is key-value store, our ability to read/write to Dynamo is much faster.
- |cloud| **Scalability**: Dynamo was designed to easily scale and handle a large number of requests.

Drawbacks of DynamoDB compapred to SQL
----------------------------------------

However, there are some draw backs.

- **Adding new features**:  Creating a DynamoDB table requires us to make many assumptions about how our access patterns will be used. If that changes in the future, we may have to undo some of our assumptions and redesign the table.
- **Joins**:  There are no joins in DynamoDB, so this makes performing some queries more difficult.
- **No query language**:  There is no official query language for DynamoDB.
- **Duplicating data**:  The data is duplicated making analytical queries difficult.

Rootski's DynamoDB Data Access Patterns
-----------------------------------------

In order to use DynamoDB this required us to detail our access patterns before
modeling our data in a DynamoDB table. The image below is a table summarizing
the main access patterns in Rootski.

.. drawio-image:: /_static/infrastructure/dynamo-actions.drawio
    :format: svg
    :target: /_images/dynamo-actions.svg

.. note:: 👆 Click this image to make it bigger.

Rootski's DynamoDB Schema
-----------------------------------------

Using these access patterns, we set up the following DynamoDB table with the following keys.

.. drawio-image:: /_static/infrastructure/dynamo-data-model.drawio
    :format: svg
    :target: /_images/dynamo-data-model.svg

.. note:: 👆 Click this image to make it bigger.

.. tip:: You can see the `original SQL Rootski schema here <https://quickest-trail-808.notion.site/Database-e8254dcaa5a04b7085fe7b35cccc10df>`_, along with screenshots of where the data is used in the frontend.
