---
layout: page
title: Tabular Reinforcement Learning
description: Solving Taxi-v3 using Q-Learning and On-Policy First Visit Monte Carlo
img: assets/img/taxi_50.gif
importance: 1
category: completed
related_publications: false
---

*Disclaimer: The code for this project is not accessible to the public as it constitutes one of the assignments for the [Reinforcement Learning](https://opencourse.inf.ed.ac.uk/rl) course at [The University of Edinburgh](https://www.ed.ac.uk/).*

# Taxi-v3

<div class="row justify-content-center">
    <div class="col-md-auto">
        {% include figure.liquid path="assets/img/taxi_50.gif" class="img-fluid rounded z-depth-1" %}
    </div>
</div>

The presented environment is part of the Toy Text environments in [Gymnasium](https://gymnasium.farama.org/), specifically the [Taxi-v3](https://gymnasium.farama.org/environments/toy_text/taxi/) environment. In this 5x5 grid world, the taxi must navigate to passengers at four designated locations (Red, Green, Yellow, and Blue), pick them up, and drop them off at their desired destinations. The action space is discrete with six possible actions, including movement in different directions, picking up, and dropping off passengers. There are 500 discrete states, considering taxi positions, passenger locations, and destination locations. The episode starts randomly, and rewards are given for successful passenger drop-offs, with penalties for incorrect pickup/drop-off actions. The episode ends when the passenger is dropped off or after 200 steps. This project uses Q-Learning and On-Policy First Visit Monte Carlo to solve the given environment.

---

## Setting up the Agent

An abstract class, `Agent`, for the agent has been implemented as a base class for both the Q-learning agent and the Monte Carlo agent. It consists of a total of four functions, two of which are abstract.

```python
class Agent(ABC):
    def __init__(
        self,
        action_space: Space,
        obs_space: Space,
        gamma: float,
        epsilon: float,
        **kwargs
    )
    def act(self, obs: int) -> int
    @abstractmethod
    def schedule_hyperparameters(self, timestep: int, max_timestep: int)
    @abstractmethod
    def learn(self)
```

The `__init__` function initializes the basic variables of the class, including:
- `action_space`: action space of the environment
- `obs_space`: observation space of the environment
- `gamma`: discount factor
- `epsilon`: epsilon for epsilon-greedy action selection
- `n_acts`: number of actions
- `q_table`: table for Q-values mapping pairs of observations and actions to respective Q-values

The `act` function takes an observation as input and uses epsilon-greedy selection to return the index of the selected action. Before each episode, the `schedule_hyperparameters` function is called to adjust epsilon. It takes current timestep at the beginning of the episode and the maximum timesteps that the training loop will run for as arguments. The `learn` function updates the Q-table based on the agent's experience.

### Q-Learning Agent

A class, `QLearningAgent`, that inherits from `Agent` has been implemented as the Q-Learning agent.

```python
class QLearningAgent(Agent):
    def __init__(self, alpha: float, **kwargs)
    def schedule_hyperparameters(self, timestep: int, max_timestep: int)
    def learn(
        self, obs: int, action: int, reward: float, n_obs: int, done: bool
    ) -> float
```

The `__init__` function initializes an additional variable called `alpha` which represents the learning rate of the agent. The `schedule_hyperparameters` function uses linear decay to adjust epsilon, using a different gradient and minumum compared to those used in the Monte Carlo agent. The `learn` function takes several arguments as input, including:
- `obs`: received observation representing the current environmental state
- `action`: index of applied action
- `reward`: received reward
- `n_obs`: received observation representing the next environmental state
- `done`: flag indicating whether a terminal state has been reached

Then, it implements the Q-Learning algorithm to return the updated Q-value for current observation-action pair.

### Monte Carlo Agent

A class, `MonteCarloAgent`, that inherits from `Agent` has been implemented as the Monte Carlo agent.

```python
class MonteCarloAgent(Agent):
    def __init__(self, **kwargs)
    def schedule_hyperparameters(self, timestep: int, max_timestep: int)
    def learn(
        self, obses: List[int], actions: List[int], rewards: List[float]
    ) -> Dict
```

The `__init__` function initializes an additional variable called `sa_counts` which is a dicionary used to count occurrences observation-action pairs. The `schedule_hyperparameters` function uses linear decay to adjust epsilon, using a different gradient and minumum compared to those used in the Q-Learning agent. The `learn` function takes several arguments as input, including:
- `obses`: list of received observations representing environmental states of trajectory (in the order they were encountered)
- `actions`: list of indices of applied actions in trajectory (in the order they were applied)
- `rewards`: list of received rewards during trajectory (in the order they were received)

Then, it implements the On-Policy First Visit Monte Carlo algorithm to return a dictionary containing the updated Q-value of all the updated state-action pairs indexed by the state action pair.

---

## Training the Agent

The environment that the agents train and evaluate on are set with the following parameters:
- `env`: "Taxi-v3"
- `eps_max_steps`: 50
- `eval_episodes`: 500
- `eval_eps_max_steps`: 100,
- `total_eps` of Monte Carlo agent: 100000
- `total_eps` of Q-Learning agent: 10000

Both agents use the same `evaluate` function, which is implemented in `utils.py` for the evaluation of agent.

```python
def evaluate(env, agent, max_steps, eval_episodes, render)
```

The function accepts 5 parameters as its arguments, which are:
- `env`: environment to execute evaluation on
- `agent`: agent to act in environment
- `max_steps`: max number of steps per evaluation episode
- `eval_episodes`: number of evaluation episodes
- `render`: flag whether evaluation runs should be rendered

The `evaluate` function assesses the given configuration on the provided environment, using the specified agent, and returns two pieces of information:
- The mean return received over all evaluation episodes.
- The number of evaluation episodes where the return was negative.

This function serves to evaluate the performance of the agent in the given environment and provides insights into its effectiveness in completing tasks and avoiding negative outcomes.

### Using Q-Learning

Training the agent with Q-Learning is done in `train_q_learning.py`. The Python file consists of two functions, `q_learning_eval` and `train`, and a few configurable constants, `eval_freq`, `alpha`, `epsilon` and `gamma`.

```python
CONFIG = {
    "eval_freq": 1000,
    "alpha": 0.5,
    "epsilon": 0.4,
    "gamma": 0.99,
}
def q_learning_eval(env,
        config,
        q_table,
        render=True,
        output=True)
def train(env, config, output=True)
```

 `q_learning_eval` accepts 5 parameters as its arguments which are:
 - env: environment to execute evaluation on
 - config: configuration dictionary containing hyperparameters
 - q_table: Q-table mapping observation-action to Q-values
 - render: flag whether evaluation runs should be rendered
 - output: flag whether mean evaluation performance should be printed

This function uses `utils.evaluate` to evaluate the configuration of Q-learning on given environment when initialised with given Q-table. Then, it returns the mean and standard deviation of returns received over episodes.

On the other hand, `train` accepts 3 parameters as its arguments which are:
- env: environment to execute evaluation on
- config: configuration dictionary containing hyperparameters
- output: flag if mean evaluation results should be printed

It trains the Q-Learning agent and calls `q_learning_eval` to evaluate on given environment with provided hyperparameters. Then, it returns the total reward over all episodes, list of means and standard deviations of evaluation returns and the final Q-table.

### Using On-Policy First Visit Monte Carlo

Training the agent with Monte Carlo is done in `train_monte_carlo.py`. The Python file consists of two functions, `monte_carlo_eval` and `train`, and a few configurable constants, `eval_freq`, `epsilon` and `gamma`.

```python
CONFIG = {
    "eval_freq": 5000,
    "epsilon": 0.3,
    "gamma": 0.99,
}
def monte_carlo_eval(env,
        config,
        q_table,
        render=True)
def train(env, config)
```

 `monte_carlo_eval` accepts 4 parameters as its arguments which are:
 - env: environment to execute evaluation on
 - config: configuration dictionary containing hyperparameters
 - q_table: Q-table mapping observation-action to Q-values
 - render: flag whether evaluation runs should be rendered

This function uses `utils.evaluate` to evaluate the configuration of Monte Carlo on given environment when initialised with given Q-table. Then, it returns the mean and standard deviation of returns received over episodes.

On the other hand, `train` accepts 2 parameters as its arguments which are:
- env: environment to execute evaluation on
- config: configuration dictionary containing hyperparameters

It trains the Monte Carlo agent and calls `monte_carlo_eval` to evaluate on given environment with provided hyperparameters. Then, it returns the total reward over all episodes, list of means and standard deviations of evaluation returns and the final Q-table.

---

## Results
