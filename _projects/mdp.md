---
layout: page
title: Markov Decision Process Solver
description: Solving Markov Decision Process with dynamic programming.
img: assets/img/decision-making.png
importance: 2
category: completed
related_publications: false
---

*Disclaimer: The code for this project is not accessible to the public as it constitutes one of the assignments for the [Reinforcement Learning course](https://opencourse.inf.ed.ac.uk/rl) at [The University of Edinburgh](https://www.ed.ac.uk/).*

# Markov Decision Process

A Markov Decision Process is a mathematical framework used to model decision-making in situations where outcomes are uncertain. It consists of the following key components:

1. **States (S)**: A set of possible situations or conditions that the system can be in.
2. **Actions (A)**: A set of possible moves or decisions that an agent can take.
3. **Transition Probabilities (P)**: The probabilities associated with moving from one state to another based on a chosen action. This reflects the uncertainty in the system.
4. **Rewards (R)**: Numeric values associated with state-action pairs, indicating the immediate benefit or cost of taking a particular action in a specific state.
5. **Policy (π)**: A strategy or plan that defines the agent's decision-making rules, specifying which action to take in each state.

The system evolves over time, with the agent selecting actions in different states, transitioning to new states, and receiving rewards. The goal is to find an optimal policy that maximizes the expected cumulative reward over time.

## Setting up the Environment

A class for MDP has been implemented. This class incorporates various class variables and functions, serving distinct roles and functionalities as detailed earlier.

```python
class MDP:
    def __init__(self)
    def add_transition(self, *transitions: List[Transition])
    def _add_transition(self, transition: Transition)
    def add_terminal_state(self, state: State)
    def add_initial_state(self, state: State)
    def ensure_compiled(self)
    def _decompile(self)
    def _compile(self)
    def render(self, filename: str)

```

As an example, this class can be used to instantiate an MDP object with three states and two actions. Additionally, the MDP's transition can be added after instantiation.

```python
    mdp = MDP()
    mdp.add_transition(        
        #         start action end prob reward
        Transition("s0", "a0", "s1", 0.4, 5),
        Transition("s0", "a0", "s2", 0.6, -3),
        Transition("s0", "a1", "s1", 0.3, 2),
        Transition("s0", "a1", "s2", 0.7, 1),
        Transition("s1", "a0", "s0", 0.1, 1),
        Transition("s1", "a0", "s2", 0.9, 2),
        Transition("s1", "a1", "s0", 0.8, -1),
        Transition("s1", "a1", "s2", 0.2, 4),
        Transition("s2", "a0", "s0", 0.6, 0),
        Transition("s2", "a0", "s1", 0.4, -5),
        Transition("s2", "a1", "s0", 0.3, 3),
        Transition("s2", "a1", "s1", 0.7, 2)
    )
```

The following represents the transition table for the example.

| Start | Action | End | Probability | Reward |
|:-----:|:------:|:---:|:-----------:|:------:|
|   s0  |   a0   |  s1 |     0.4     |    5   |
|   s0  |   a0   |  s2 |     0.6     |   -3   |
|   s0  |   a1   |  s1 |     0.3     |    2   |
|   s0  |   a1   |  s2 |     0.7     |    1   |
|   s1  |   a0   |  s0 |     0.1     |    1   |
|   s1  |   a0   |  s2 |     0.9     |    2   |
|   s1  |   a1   |  s0 |     0.8     |   -1   |
|   s1  |   a1   |  s2 |     0.2     |    4   |
|   s2  |   a0   |  s0 |     0.6     |    0   |
|   s2  |   a0   |  s1 |     0.4     |   -5   |
|   s2  |   a1   |  s0 |     0.3     |    3   |
|   s2  |   a1   |  s1 |     0.7     |    2   |

## Dynamic Programming

Two dynamic programming algorithms, namely value iteration and policy iteration, are used to solve Markov Decision Processes (MDPs).

A class called ```MDPSolver``` has been implemented as an abstract class for the mentioned algorithms. This class includes a constructor, a class function, and an abstract function.

```python
class MDPSolver(ABC):
    def __init__(self, mdp: MDP, gamma: float)
    def decode_policy(self, policy: Dict[int, np.ndarray]) -> Dict[State, Action]
    @abstractmethod
    def solve(self)
```

### Value Iteration

The Value Iteration algorithm is implemented as ```ValueIteration(MDPSolver)```. This implementation includes three functions, with one of them specifically implementing the ```solve``` function inherited from its parent class.

```python
class ValueIteration(MDPSolver):
    def _calc_value_func(self, theta: float) -> np.ndarray
    def _calc_policy(self, V: np.ndarray) -> np.ndarray
    def solve(self, theta: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]
```

### Policy Iteration

The Policy Iteration algorithm is implemented as ```PolicyIteration(MDPSolver)```. This implementation includes three functions, with one of them specifically implementing the ```solve``` function inherited from its parent class.

```python
class PolicyIteration(MDPSolver):
    def _policy_eval(self, policy: np.ndarray) -> np.ndarray
    def _policy_improvement(self) -> Tuple[np.ndarray, np.ndarray]
    def solve(self, theta: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]
```

## Solving MDP with Dynamic Programming


