.. _architecture-page:

==========================
Architecture & Tech Stack
==========================

.. toctree::
   :hidden:

   frontend/index

   database/index

.. drawio-image:: ./rootski-architecture.drawio
    :format: svg
    :target: /_images/rootski-architecture.svg

.. note:: 👆 Click this image to make it bigger.

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

rootski is architected...

- |flag| with awesome practices!
- |users| to scale to thousands of concurrent users
- |dollar| to be cheap to run (~$20-30/mo)
- |secure| to be secure (data is backed up and secured, contributors and scripts
  have minimum-required access, network access and credentials are gated)
- |ghost| to be ephemeral: any piece of the architecture can be destroyed at any time
  and be recovered very quickly using code

Architecture Walkthrough
----------------------------------------------

This video explains the architecture in a way that is meant to be accessible
to people who are new to software architecture and running things in the cloud.

.. note::

    Most of this video is true to the architecture diagram above, but we
    have replaced the spot instance backend with API Gateway and a lightsail instance.

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/vlgTCXt9pBU"
      title="YouTube video player" frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen>
    </iframe>
