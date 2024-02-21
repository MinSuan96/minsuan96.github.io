---
layout: post
title: Gradient Descent with Python
date: 2024-02-21
description: A little warm up before my big project.
tags: Python
# categories: sample-posts
giscus_comments: false
related_posts: false
---

{::nomarkdown}
{% assign jupyter_path = "assets/jupyter/gradient-descent.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/gradient-descent.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
