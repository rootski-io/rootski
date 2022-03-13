.. |br| raw:: html

      <br>

{% set split_name = fullname.split(".") %}
{{ split_name[-1] | escape | underline}}

.. automodule:: {{ fullname }}



{% block attributes %}
{% if attributes %}

|br|
|br|
|br|

.. .. rubric:: Module Attributes

Module Attributes
--------------------------


.. autosummary::
{% for item in attributes %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}








{% block constants %}
{% if attributes %}


{% for item in attributes %}
   {% if (item | upper) == item %}
.. autodata:: {{ item }}
   {% endif %}
{%- endfor %}
{% endif %}
{% endblock %}






{% block functions %}
{% if functions %}

|br|
|br|
|br|

.. .. rubric:: Functions

Functions
--------------------------

.. autosummary::
   :nosignatures:
{% for item in functions %}
   {{ item }}
{%- endfor %}

{% for function in functions %}
{% set split_func_name = function.split(".") %}
{{ ("``" + split_func_name[-1] + "()``") }}
{{ "~" * 100 }}

.. autofunction:: {{ function }}
{%- endfor %}

{% endif %}
{% endblock %}





{% block exceptions %}
{% if exceptions %}

|br|
|br|
|br|

.. .. rubric:: Exceptions

Exceptions
--------------------------

.. autosummary::

   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
{% endif %}
{% endblock %}






{% block modules %}
{% if modules %}

|br|
|br|
|br|

.. autosummary::
   :toctree:
   :template: module-template.rst
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}



{% block classes %}
{% if classes %}

|br|
|br|
|br|

.. .. rubric:: Classes

Classes
--------------------------

.. autosummary::
   :template: class-template.rst
   :nosignatures:
{% for item in classes %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% for class in classes %}
{{ ("``class " + class + "``") }}
{{ "~" * 100 }}

.. autoclass:: {{ class }}
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __call__, __add__, __mul__

   .. autosummary::
      :nosignatures:

      {% for attribute in class["attributes"] %}
      ~{{ class }}.{{ attribute }}
      {% endfor %}
{% endfor %}
