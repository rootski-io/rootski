.. _home:

==========================================================================
Knowledge Base
==========================================================================

.. image:: /breakdown-window.svg
  :alt: russian word broken into roots

.. toctree::
  :hidden:
  :maxdepth: 1

  Home <self>
  Onboarding <rst/onboarding/index>
  Architecture & Tech Stack <rst/architecture/index>

.. toctree::
  :hidden:
  :maxdepth: 1
  :caption: Explore the codebase!

  Backend API Reference <rootski-api-reference>
  Infrastructure as Code Reference <iac-reference>


.. repository badges
.. raw:: html

   </br>

   <!-- badges:
   - build pass/fail (built into GitHub)
   - coverage percentage (provided by codecov) -->
   <img alt="build" src="https://github.com/rootski-io/rootski/actions/workflows/rootski-ci.yml/badge.svg" />
   <a href="https://codecov.io/gh/rootski-io/rootski">
      <img alt="codecov" src="https://codecov.io/gh/rootski-io/rootski/branch/trunk/graph/badge.svg?token=YZJ0UFXNU3">
   </a>
   <br />
   <br />

Helpful Links
-------------

.. directive to force insert some spaces
.. |tab| raw:: html

   &nbsp;&nbsp;

.. directives to insert font-awesome icons; see conf.py:html_css_files
.. |rootski| raw:: html

   <i class="fab fa-r fa-2x" style="color: #03a9f4"></i>

.. |youtube| raw:: html

   <i class="fab fa-youtube fa-2x" style="color: red"></i>

.. |aws| raw:: html

   <i class="fab fa-aws fa-2x" style="color: orange"></i>

.. |slack| raw:: html

   <i class="fab fa-slack fa-2x" style="color: purple"></i>

.. |clickup| raw:: html

   <i class="fa-solid fa-bars-progress fa-2x" style="color: magenta"></i>

.. |github| raw:: html

   <i class="fab fa-github fa-2x" style="color: gray"></i>

.. |linkedin| raw:: html

   <i class="fab fa-linkedin fa-2x" style="color: #0077b5"></i>

.. list-table::
   :widths: 10 30 60

   * - |rootski|
     - `rootski.io <https://www.rootski.io/>`_
     - The live application we're building!
   * - |github|
     - `GitHub repo <https://github.com/rootski-io/rootski>`_
     - Leave us a star ⭐️. The codebase; everything is open-source except for the full rootski dataset.
   * - |clickup|
     - `ClickUp Board <https://sharing.clickup.com/l/h/4-30114956-1/80ea8d248c817f3>`_
     - Kanban board and backlog of work being done on rootski.
   * - |slack|
     - `Slack <https://join.slack.com/t/rootskiio/shared_invite/zt-13avx8j84-mocJVx5wFAGNf5wUuy07OA>`_
     - Chat for anything related to rootski, onboarding, and projects.
   * - |youtube| |tab|
     - `YouTube Playlist <https://www.youtube.com/playlist?list=PLwF2z4Iu4rabmY7RbRNetjZprLfe8qWNz>`_
     - Training videos walking through the architecture, tools, and how to contribute to rootski.
   * - |linkedin|
     - `LinkedIn Page <https://www.linkedin.com/company/rootski/>`_
     - Follow our page 🔔. This is the rootski company page where we share posts
       promoting the contributors after each PR.
   * - |aws|
     - `AWS console <https://rootski.signin.aws.amazon.com/console>`_
     - Sign in link for the rootski AWS account.


Contributors ✨
------------------

rootski is developed by volunteers! This `emoji key <https://allcontributors.org/docs/en/emoji-key>`_
labels the different types of contributions.

Links to everyone's personal sites are on the `GitHub README <https://github.com/rootski-io/rootski>`_ 🙂.

.. raw:: html
    :file: ../../CONTRIBUTORS.md


What is rootski?
---------------------

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/_KYgVet_HEA"
      title="YouTube video player" frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen>
    </iframe>

rootski is an open-source, full-stack AI application for learning Russian.

The three reasons for open-sourcing the rootski project are to:

1. make `rootski.io <https://www.rootski.io/>`_ development faster and more fun.

2. create a public reference anyone can see of an production-grade A.I. application
   made with the absolute best industry practices.

   .. note:: If you'd like to see how rootski is built, check out the :ref:`Architecture & Tech Stack <architecture-page>`.

3. **offer mentorship and real-world experience** to contributors at *any* experience level
   that are hard to simulate on a solo personal project--whether that be in

   - full-stack development
   - deploying software in AWS
   - developing data science models and "shipping" them
   - UI/UX
   - DevOps
   - MLOps
   - ... anything else that goes into making a A.I. application with a large user base 😃.

   .. note::

      If you would like to contribute, welcome 🎉 🎉!! Any experience level is welcome as long as you
      are `willing to learn <https://www.linkedin.com/posts/eric-riddoch_im-willing-to-learn-candidates-for-ds-activity-6895803295609233408-dKmu>`_. Check out the :ref:`onboarding page <onboarding-page>`
      get started.



.. .. warning::

..    **Disclaimer, please read!** Contributing is 100% "free labor" in the sense that
..    Eric Riddoch owns the rootski project.

..    Please *do* or please *don't* contribute based on what you think is best for your
..    career and personal growth.

..    The value of contributing to rootski is in getting to work on part of a real product,
..    having mentorship, and experimenting with tools you don't use at your day job. Whether
..    or not you're experienced, that "mentorship" looks exactly the way it would at a paid
..    job: we're a bunch of non-experts working mostly asynchronously, some of us knowing more about certain
..    technologies than others.

..    For Eric, this project is about learning/mentoring and he'd rather move slowly so
..    that people can learn rather than focus on exploiting people adding new features.

..    Eric pays $20+/mo (sometimes $50) on this and earns nothing. If that ever changes,
..    he will be clear about that. If anyone were to be paid to work on this, the project
..    simply wouldn't be possible. Eric is happy if the work we're doing here does nothing
..    more than give people career opportunities and help remove confusion about how "real"
..    software is built.

..    Many of the contributors make real sacrifices offering their time and mentorship
..    working on this project. Please don't criticize our motives. We want you do do what's
..    best for you.  This model for building a product was inspired by this
..    `podcast interview with the creator of the Python discord channel
..    <https://talkpython.fm/episodes/show/305/python-community-at-python-discord>`_.

..    Eric finds their intentions to be genuine. Please know that for over a year,
..    Eric has "sunk" many evenings and weekends mentoring engineers and has seen no
..    personal "return on investment" outside of relationships; he will gladly continue
..    to do so, time permitting.

..    Feel free to reach out to any of the "Contributors" or "Friends" to ask them
..    about their experience.
