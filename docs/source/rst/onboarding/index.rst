.. _onboarding-page:

======================
Onboarding Guide
======================

.. note::

   🌙 The dropdowns on this page don't display well in dark mode.

   You can switch to light mode by clicking on the "🌞" button at the top-right of the page.

If you are considering contributing, welcome!!

rootski is run like a tech startup, so the onboarding process feels similar
to starting a new job.

The onboarding process will guide you through...

- 💬 introducing yourself
- ⚡️ getting access to systems (Slack, ClickUp, GitHub, AWS, etc.)
- ⚙️ setting up your development environment
- 🧱 familiarizing yourself with the rootski architecture and our development practices
- 😎 picking up your first project!
- 📚 (if you want) creating a learning plan to get the skills you need for your project

The process is completely asynchronous so you can take it as fast or slow as you like 🙂.

Why contribute?
-----------------

.. dropdown:: ⚠️ Disclaimer, please read!
   :title: bg-warning
   :animate: fade-in

   Contributing is 100% "free labor" in the sense that Eric Riddoch owns the rootski project.

   **Please *do* or please *don't* contribute based on what you think is best for your career and
   personal growth.**

   The value of contributing to rootski is in getting to work on part of a
   real product, having mentorship, and experimenting with tools you don't use at your day job.
   Whether or not you're experienced, that "mentorship" looks exactly the way it would at a paid
   job: we're a bunch of non-experts working together, some of us knowing more about certain technologies
   than others.

   For Eric, this project is about learning/mentoring. He'd prefer to move slowly
   so that people can learn rather than push people beyond what they are comfortable with.

   Eric pays $20+/mo (sometimes $50) on this and earns nothing. If that ever changes,
   he will be clear about that. If anyone were to be paid to work on this, the project
   simply wouldn't be possible. Eric is happy if the work we're doing here does nothing
   more than give people career opportunities and help remove confusion about how "real"
   software is built.

   Many of the contributors make sacrifices offering their time and mentorship working
   on this project. Please don't criticize our motives. We truly do want you do do
   what's best for you. This model for building a product was inspired by this
   `podcast interview with the creator of the Python discord channel
   <https://talkpython.fm/episodes/show/305/python-community-at-python-discord>`_.

   Eric finds their intentions to be genuine. Please know that for over a year,
   Eric has "sunk" many evenings and weekends mentoring engineers and has seen no
   personal "return on investment" outside of relationships; he will gladly continue
   to do so, time permitting.

   Feel free to reach out to any current or past contributors to ask them about
   their experience.

Fun, motivational story
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. dropdown:: No need to read this if the amount of text is overwhelming 🤣
   :animate: fade-in

   Hi! This is Eric... writing in the first person, now 🤣.

   This is the original rootski architecture from late 2020.

   I entirely credit
   this diagram for getting my current job (which I love) and my recent promotion
   to "senior" engineer.

   .. image:: /_static/old-architecture.jpeg
      :alt: Original architecture of rootski on AWS
      :target: /_static/old-architecture.jpeg

   I majored in math and took a handful of software classes at BYU in the USA.

   During school, I worked as a B.I. analyst building dashboards with SQL
   and then worked on a data engineering team for a year.

   Before and during this,
   I took some cheap 3-5-day online coding courses and made several
   `small passion projects <https://ericriddoch.info>`_. These did a lot to
   help people take me seriously enough as a "coder" to get that first data engineering job.

   I had a lot of fun building my projects, but by early 2019 I was tired of making "toy"
   data science / software apps that no one used. I had been working on a mobile app
   version of rootski before that, and I decided to pick it up more seriously.

   Through a connection at BEN (my current job), I started interviewing for an "MLOps"
   position. I had been working on rootski at the time and sent people on the team
   this diagram of what I was building.

   When my current manager and some other team members saw this, the interviews stopped.
   The rest of our calls turned into "is this job something that *you* want?"
   It was awesome 😃. That was the first time I'd been treated like that when interviewing.
   Since then, rootski has come a long way and I've learned a *ton*.

   rootski has given me fantastic experience with some advanced software/data science concepts like
   "infrastructure as code", "continuous deployment", "functional testing",
   "container orchestration", "deploying models", tracking data science experiments,
   security, structuring a frontend and backend codebase, and a whole bunch of other things.

   Multiple times, I've felt like a genius at work when problems come up that I
   have already solved with rootski. I have copy/pasted portions of the rootski codebase
   that took days of thought to solve the same problems again in less than an hour.
   That's such a cool feeling, hahaha.

   It's my opinion that in tech,

   .. math::

      \text{years-of-experience} \neq \text{skill or seniority}

   Not everyone agrees with this, but enough do that my work with rootski has
   given me a lot of cool opportunities.

   I used to pair-program with people from school or LinkedIn to help them get
   started with similar things, but it became too time-consuming. Now, I use rootski as
   shared personal project with lots of asynchronous resources for less experienced people.

   At first, rootski was my solution to the "how do I get a job without experience and
   how do I get experience without a job?" problem. Now it's my outlet to play with
   tools I don't use at my day job and mentor people.

   I'd be stoked if, at some point, some paid component of rootski could start
   making enough money to pay for the infrastructure costs, but I'm not too hung up over that.
   For me, working on this has *easily* paid for itself in job opportunities, raises, and fun.

Things to help your career
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want contributing to be awesome for your career. This is a constant topic of discussion in our chat.

Here are some of the current initiatives to benefit contributors:

#. 🔎 **Giving meticulous, constructive code reviews**

   Getting comments from more experienced engineers is extremely beneficial.
   It tends to be harder to get this kind of attention on your code when you build things solo.

#. 🙌 **Posting contributor spotlights on our** `LinkedIn Page <https://www.linkedin.com/company/rootski/>`_

   These are short writeups about each PR (or other contribution). We could do the same with Twitter. The posts...

   - spotlight the contributor and how they achieved what they did
   - tag the contributor at the top and several other contributors/followers at the end
   - ask contributors to share the post to their networks
   - link to the PR, a preview, or something else people can see

#. 👩‍💼 **Defining job titles that contributors can post on Linkedin**

   After completing your first non-onboarding ticket, you can list rootski either as a
   "work experience" or as a "project" on your LinkedIn profile.

#. 🔗 **Open-sourcing the codebase**

   This way, contributors can show off their work by sharing links to exact
   files, commits, PRs, etc.

   Everything that can be public will be. The most sensitive,
   proprietary part of rootski is the dataset, so we made only made a subset
   of that open-source.

#. 🌄 **Promoting everyone's pictures, LinkedIn profiles, contact info, etc. on...**

   - [To do] `rootski.io <https://www.rootski.io>`_
   - The `GitHub README <https://github.com/rootski-io/rootski>`_
   - The :ref:`homepage <home>` of the knowledge base
   - Anywhere else that makes sense 😃


How to get started
---------------------

We keep track of the ongoing/upcoming work on rootski using a "ticket board" tool called `ClickUp <https://www.clickup.com>`_

The onboarding process works the same way 😃.

Reach out to Eric on Slack to create a set of onboarding tasks for you on our ClickUp board.

In the meantime, we have copies of most of the tasks we will generate for you right here!

They go roughly in the order you should prioritize them.

.. dropdown:: 💬 Join Slack - Do this first!
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/slack.md
      :parser: myst_parser.sphinx_

.. dropdown:: 💻 Get GitHub access
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/github.md
      :parser: myst_parser.sphinx_

.. dropdown:: ✉️ Get ClickUp access
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/clickup.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🧱 Familiarize yourself with the rootski architecture
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/architecture.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🐧 Brush up on Linux and bash
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/linux-and-bash.md
      :parser: myst_parser.sphinx_

.. dropdown:: ⚡️ Set up ZSH
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/zsh.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🐍 Install Python the "right" way
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/python.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🐳 Install Docker
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/docker-desktop.md
      :parser: myst_parser.sphinx_

.. dropdown:: ✏️ Set up your code editor
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/vscode.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🐿 Install DBeaver to connect to the database
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/dbeaver.md
      :parser: myst_parser.sphinx_

.. dropdown:: 🌲 Learn how we work with git (trunk-based development)
   :animate: fade-in
   :title: font-weight-bold

   .. include:: /_static/infrastructure/onboarding-tasks/trunk-based-development.md
      :parser: myst_parser.sphinx_
