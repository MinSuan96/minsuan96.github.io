---
layout: page
title: Tabular Reinforcement Learning
description: Solving Taxi-v3 using Q-Learning and On-policy first-visit Monte Carlo
img: assets/img/taxi_50.gif
importance: 1
category: completed
related_publications: false
---

*Disclaimer: The code for this project is not accessible to the public as it constitutes one of the assignments for the [Reinforcement Learning](https://opencourse.inf.ed.ac.uk/rl) course at [The University of Edinburgh](https://www.ed.ac.uk/).*

# Taxi-v3

<div class="row justify-content-center">
    <div class="col-md">
        {% include figure.liquid path="assets/img/taxi_50.gif" title="Render of Taxi-v3" class="img-fluid rounded z-depth-1" %}
    </div>
</div>

The presented environment is part of the Toy Text environments in [Gymnasium](https://gymnasium.farama.org/), specifically the [Taxi-v3](https://gymnasium.farama.org/environments/toy_text/taxi/) environment. In this 5x5 grid world, the taxi must navigate to passengers at four designated locations (Red, Green, Yellow, and Blue), pick them up, and drop them off at their desired destinations. The action space is discrete with six possible actions, including movement in different directions, picking up, and dropping off passengers. There are 500 discrete states, considering taxi positions, passenger locations, and destination locations. The episode starts randomly, and rewards are given for successful passenger drop-offs, with penalties for incorrect pickup/drop-off actions. The episode ends when the passenger is dropped off or after 200 steps. The environment provides information such as transition probability and action masks, offering a comprehensive setting for reinforcement learning tasks.

## Setting up the Environment


