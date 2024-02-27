---
layout: page
title: Gymnasium Playground
description: Solving multiple environments in Gymnasium using Reinforcement Learning.
img: assets/img/reinforcement-learning.png
importance: 1
category: completed
related_publications: false
---

*Disclaimer: The code for this project is not accessible to the public as it constitutes one of the assignments for the [Reinforcement Learning course](https://opencourse.inf.ed.ac.uk/rl) at [The University of Edinburgh](https://www.ed.ac.uk/).*

[Gymnasium](https://gymnasium.farama.org/) is an API standard for single-agent reinforcement learning environments, with popular reference environments and related utilities. This project revolves around my approach to addressing challenges in multiple environments within Gymnasium.

# Markov Decision Process

Before we dig into solving environments in Gymnasium, let's quickly talk about [Markov Decision Processes](https://en.wikipedia.org/wiki/Markov_decision_process) (MDP) and how we can handle them with dynamic programming. 

A Markov Decision Process is a mathematical framework used to model decision-making in situations where outcomes are uncertain. It consists of the following key components:

1. **States (S)**: A set of possible situations or conditions that the system can be in.
2. **Actions (A)**: A set of possible moves or decisions that an agent can take.
3. **Transition Probabilities (P)**: The probabilities associated with moving from one state to another based on a chosen action. This reflects the uncertainty in the system.
4. **Rewards (R)**: Numeric values associated with state-action pairs, indicating the immediate benefit or cost of taking a particular action in a specific state.
5. **Policy (π)**: A strategy or plan that defines the agent's decision-making rules, specifying which action to take in each state.

The system evolves over time, with the agent selecting actions in different states, transitioning to new states, and receiving rewards. The goal is to find an optimal policy that maximizes the expected cumulative reward over time.

## Setting up the Environment

A base class for MDP is created. The class has several class variables and class functions.



## Solving MDPs with Dynamic Programming

Two dynamic programming algorithms, namely value iteration and policy iteration, can be employed to solve Markov Decision Processes (MDPs).

### Value Iteration

### Policy Iteration
