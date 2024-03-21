---
layout: page
title: Deep Reinforcement Learning in Discrete Action Space
description: Solving CartPole and Acrobot using Deep Q-Networks and REINFORCE
img: assets/img/acrobot_cartpole.gif
importance: 1
category: Writing in Progress
related_publications: false
---

*Disclaimer: The code for this project is not accessible to the public as it constitutes one of the assignments for the [Reinforcement Learning](https://opencourse.inf.ed.ac.uk/rl) course at [The University of Edinburgh](https://www.ed.ac.uk/).*

- [The Environment](#the-environment)
  - [Cartpole](#cartpole)
  - [Acrobot](#acrobot)
- [Setting up the Agent](#setting-up-the-agent)
- [Training the Agent](#training-the-agent)
- [Results](#results)
  - [Cartpole](#cartpole-1)
    - [DQN](#dqn)
    - [REINFORCE](#reinforce)
  - [Acrobot](#acrobot-1)
    - [DQN](#dqn-1)
    - [REINFORCE](#reinforce-1)

# The Environment

<div class="container">
    <div class="row justify-content-center">
        <div class="col">
            {% include figure.liquid path="assets/img/cartpole.gif" class="img-fluid rounded z-depth-1" %}
        </div>
        <div class="col">
            {% include figure.liquid path="assets/img/acrobot.gif" class="img-fluid rounded z-depth-1" %}
        </div>
    </div>
</div>

This project tackles two classic control problems: the [Cartpole](https://gymnasium.farama.org/environments/classic_control/cart_pole/) and [Acrobot](https://gymnasium.farama.org/environments/classic_control/acrobot/) environments.

## Cartpole

The Cart Pole environment, part of the Classic Control environments, simulates a scenario where a pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. The goal is to balance the pole by applying forces in the left or right direction to the cart.

At the start of each episode, the pole is placed upright on the cart, and the agent must take actions to prevent the pole from falling over. The action space is discrete with two possible actions:

- 0: Push the cart to the left
- 1: Push the cart to the right

The observation space is a continuous array with four elements:

1. Cart Position: Ranges from -4.8 to 4.8
2. Cart Velocity: Can take any real value
3. Pole Angle: Ranges from approximately -24° to 24°
4. Pole Angular Velocity: Can take any real value

However, episode termination occurs if the cart position leaves the range of -2.4 to 2.4 or if the pole angle exceeds approximately ±12°.

The agent receives a reward of +1 for each step taken, including the termination step, as the goal is to keep the pole upright for as long as possible. The episode ends if any of the following conditions are met:

1. The pole angle exceeds approximately ±12°.
2. The cart position reaches the edge of the display, exceeding ±2.4.
3. The episode length exceeds a predefined limit of 500 steps.

## Acrobot

The Acrobot environment is a classic control problem based on [Sutton's work](https://papers.nips.cc/paper/1995/hash/8f1d43620bc6bb580df6e80b0dc05c48-Abstract.html) in reinforcement learning. It features a system consisting of two links connected linearly to form a chain, with one end of the chain fixed. The joint between the two links is actuated, and the goal is to swing the free end of the chain above a given height while starting from an initial state where both links are hanging downwards.

In the Acrobot environment, the action space is discrete, with three possible actions representing the torque applied on the actuated joint between the two links:

- 0: Apply -1 torque to the actuated joint
- 1: Apply 0 torque to the actuated joint
- 2: Apply 1 torque to the actuated joint

The observation space is a continuous array with six elements providing information about the rotational joint angles and their angular velocities. These observations include:

1. Cosine and sine of theta1 (angle of the first joint)
2. Cosine and sine of theta2 (angle of the second joint relative to the first)
3. Angular velocity of theta1
4. Angular velocity of theta2

The episode ends when either the free end of the chain reaches a designated target height or the episode length exceeds a predefined limit. The reward structure encourages the system to reach the target height in as few steps as possible, with a reward of -1 given for each step that does not reach the goal. Achieving the target height results in termination with a reward of 0.

# Setting up the Agent

# Training the Agent

# Results

## Cartpole

### DQN

<!-- <div class="container">
    <div class="row justify-content-center">
        <div class="col">
            {% include figure.liquid path="assets/img/" class="img-fluid rounded z-depth-1" %}
        </div>
        <div class="col">
            {% include figure.liquid path="assets/img/" class="img-fluid rounded z-depth-1" %}
        </div>
        <div class="col">
            {% include figure.liquid path="assets/img/" class="img-fluid rounded z-depth-1" %}
        </div>
    </div>
    <div class="caption">
        DQN Agent trained with ,  and  episodes.
    </div>
</div> -->

### REINFORCE

## Acrobot

### DQN

### REINFORCE
