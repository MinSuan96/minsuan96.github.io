---
layout: post
title: Gradient Descent with Jupyter Notebook
date: 2024-02-21
description: A little warm up before my big project.
tags: Python
# categories: sample-posts
giscus_comments: false
related_posts: false
---

Before delving directly into the algorithm, let me provide a brief explanation of what gradient descent entails. Gradient descent is an optimization algorithm commonly used in machine learning and numerical optimization to minimize a function. The main idea behind gradient descent is to iteratively adjust the parameters of a model in the direction that reduces the value of a cost function.

Here's a step-by-step explanation of how gradient descent is done:
- Initialize Parameters: Start with an initial set of parameters for the model. These parameters could be weights in a neural network or coefficients in a linear regression model.

- Calculate the Cost Function: Evaluate the cost function, which is a measure of how well the model is performing with the current set of parameters. The goal is to minimize this cost function.

- Calculate the Gradient: Compute the gradient of the cost function with respect to each parameter. The gradient represents the direction of the steepest increase in the cost function. Mathematically, it involves taking the partial derivative of the cost function with respect to each parameter.

- Update Parameters: Adjust the parameters in the opposite direction of the gradient. This is done to move towards the minimum of the cost function. The update is performed using the learning rate, which determines the size of the steps taken in the parameter space.

    > New Parameter = Old Parameter − Learning Rate × Gradient

    The learning rate is a hyperparameter that needs to be carefully chosen. If it's too small, the algorithm may take a long time to converge, and if it's too large, it may overshoot the minimum.

- Repeat: Repeat steps 2-4 until convergence or a predetermined number of iterations. Convergence occurs when the parameters reach values where further adjustments don't significantly improve the cost function.

There are different variants of gradient descent, such as stochastic gradient descent (SGD) and mini-batch gradient descent, which involve using subsets of the training data for each iteration to reduce computational complexity. Additionally, more advanced optimization algorithms like Adam and RMSprop include adaptive learning rates to improve convergence speed. However, for this blog, I will only be using the basic gradient descent. Nevertheless, in this blog, I will implement the basic gradient descent.

{::nomarkdown}
{% assign jupyter_path = "assets/jupyter/gradient-descent.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/gradient-descent.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
