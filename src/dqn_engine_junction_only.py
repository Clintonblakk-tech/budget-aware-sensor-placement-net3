import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import random
import copy
import time
from collections import deque

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import wntr
import networkx as nx

# =====================================================
# ENVIRONMENT
# =====================================================

class SensorPlacementEnvironment:

    def __init__(
        self,
        network_file,
        sensor_budget,
        coverage_radius=2,
        coverage_weight=1.0,
        centrality_weight=0.0,
    ):

        self.sensor_budget = sensor_budget
        self.coverage_radius = coverage_radius
        self.coverage_weight = coverage_weight
        self.centrality_weight = centrality_weight

        self.wn = wntr.network.WaterNetworkModel(
            network_file
        )

        self.G = self.wn.to_graph()

        # Junction-only sensor candidate set.
        # Retain the full graph for topology and centrality calculations.
        self.nodes = list(self.wn.junction_name_list)
        self.junction_set = set(self.nodes)

        # Confirm that every eligible junction exists in the graph.
        missing_junctions = self.junction_set - set(self.G.nodes())
        if missing_junctions:
            raise ValueError(
                f"Junctions missing from graph: {sorted(missing_junctions)}"
            )

        # A sensor budget cannot exceed the number of eligible junctions.
        if not 1 <= self.sensor_budget <= len(self.nodes):
            raise ValueError(
                f"Invalid sensor budget {self.sensor_budget}. "
                f"Available junctions: {len(self.nodes)}"
            )

        self.degree = nx.degree_centrality(
            self.G
        )

        self.reset()

    def reset(self):

        self.selected_nodes = []

        return self.get_state()

    def get_state(self):

        state = np.zeros(
            len(self.nodes),
            dtype=np.float32
        )

        for node in self.selected_nodes:

            idx = self.nodes.index(node)

            state[idx] = 1.0

        return state

    def compute_coverage(self):

        # Measure coverage over eligible junctions only.
        covered_junctions = set()

        for sensor in self.selected_nodes:

            reachable = nx.single_source_shortest_path_length(
                self.G,
                sensor,
                cutoff=self.coverage_radius
            )

            covered_junctions.update(
                set(reachable.keys()).intersection(self.junction_set)
            )

        return len(covered_junctions)

    def step(self, action):

        if not isinstance(action, (int, np.integer)):
            raise TypeError(
                f"Action index must be an integer; received {type(action).__name__}."
            )

        if not 0 <= int(action) < len(self.nodes):
            raise ValueError(
                f"Invalid action index {action}. "
                f"Valid junction action indices are 0 to {len(self.nodes) - 1}."
            )

        chosen_node = self.nodes[int(action)]

        if chosen_node not in self.junction_set:
            raise ValueError(
                f"Selected node {chosen_node!r} is not an eligible junction."
            )

        if chosen_node in self.selected_nodes:

            return (
                self.get_state(),
                -1.0,
                True
            )

        self.selected_nodes.append(
            chosen_node
        )

        coverage_score = (
            self.compute_coverage()
            / len(self.nodes)
        )

        centrality_score = np.mean(
            [
                self.degree[n]
                for n in self.selected_nodes
            ]
        )

        reward = (
    self.coverage_weight * coverage_score
    +
    self.centrality_weight * centrality_score
)

        done = (
            len(self.selected_nodes)
            >= self.sensor_budget
        )

        return (
            self.get_state(),
            reward,
            done
        )

# =====================================================
# DQN NETWORK
# =====================================================

class DQN(nn.Module):

    def __init__(
        self,
        state_dim,
        action_dim
    ):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(state_dim, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, action_dim)

        )

    def forward(self, x):

        return self.network(x)

# =====================================================
# REPLAY BUFFER
# =====================================================

class ReplayBuffer:

    def __init__(self, capacity):

        self.buffer = deque(
            maxlen=capacity
        )

    def push(
        self,
        state,
        action,
        reward,
        next_state,
        done
    ):

        self.buffer.append(
            (
                state,
                action,
                reward,
                next_state,
                done
            )
        )

    def sample(
        self,
        batch_size
    ):

        batch = random.sample(
            self.buffer,
            batch_size
        )

        states, actions, rewards, next_states, dones = zip(*batch)

        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones)
        )

    def __len__(self):

        return len(self.buffer)

# =====================================================
# DQN ENGINE
# =====================================================

def run_dqn(
    network_name,
    network_file,
    sensor_budget,
    seed,
    episodes=1000,

    coverage_weight=0.70,
    centrality_weight=0.30,

    replay_buffer=True,
    target_network=True
):

    random.seed(seed)

    np.random.seed(seed)

    torch.manual_seed(seed)

    start_time = time.time()

    env = SensorPlacementEnvironment(
        network_file=network_file,
        sensor_budget=sensor_budget,
        coverage_weight=coverage_weight,
        centrality_weight=centrality_weight
    )

    state_dim = len(env.nodes)

    action_dim = len(env.nodes)

    online_net = DQN(
        state_dim,
        action_dim
    )

    target_net = copy.deepcopy(
        online_net
    )

    optimizer = optim.Adam(
        online_net.parameters(),
        lr=0.0005
    )

    loss_fn = nn.MSELoss()

    buffer = ReplayBuffer(
        50000
    )

    epsilon = 1.0
    epsilon_end = 0.01
    epsilon_decay = 0.995

    gamma = 0.99

    best_reward = -9999

    reward_history = []

    print("\n========================")
    print("DQN ENGINE")
    print("========================")

    print(f"Network : {network_name}")
    print(f"Nodes   : {state_dim}")
    print(f"Budget  : {sensor_budget}")
    print(f"Episodes: {episodes}")

    for episode in range(episodes):

        state = env.reset()

        done = False

        episode_reward = 0

        while not done:

            # ==================================
            # ACTION SELECTION
            # ==================================

            if random.random() < epsilon:

                valid_actions = np.where(
                    state == 0
                )[0]

                action = random.choice(
                    valid_actions.tolist()
                )

            else:

                with torch.no_grad():

                    q_values = online_net(
                        torch.FloatTensor(
                            state
                        ).unsqueeze(0)
                    )[0]

                    invalid_actions = np.where(
                        state == 1
                    )[0]

                    for idx in invalid_actions:

                        q_values[idx] = -1e9

                    action = torch.argmax(
                        q_values
                    ).item()

            # ==================================
            # ENVIRONMENT STEP
            # ==================================

            next_state, reward, done = env.step(
                action
            )

            buffer.push(
                state,
                action,
                reward,
                next_state,
                done
            )

            state = next_state

            episode_reward += reward

            # ==================================
            # LEARNING
            # ==================================

            if replay_buffer and len(buffer) >= 64:

                (
                    states,
                    actions,
                    rewards,
                    next_states,
                    dones
                ) = buffer.sample(64)

                states = torch.FloatTensor(
                    states
                )

                actions = torch.LongTensor(
                    actions
                )

                rewards = torch.FloatTensor(
                    rewards
                )

                next_states = torch.FloatTensor(
                    next_states
                )

                dones = torch.FloatTensor(
                    dones
                )

                current_q = online_net(
                    states
                ).gather(
                    1,
                    actions.unsqueeze(1)
                ).squeeze(1)

                with torch.no_grad():

                    if target_network:

                        next_q = target_net(
                            next_states
                        ).max(
                            dim=1
                        )[0]

                    else:

                        next_q = online_net(
                            next_states
                        ).max(
                            dim=1
                        )[0]

                    target_q = (
                        rewards
                        +
                        gamma *
                        next_q *
                        (1 - dones)
                    )

                loss = loss_fn(
                    current_q,
                    target_q
                )

                optimizer.zero_grad()

                loss.backward()

                optimizer.step()

        epsilon = max(
            epsilon_end,
            epsilon * epsilon_decay
        )

        reward_history.append(
            episode_reward
        )

        if episode_reward > best_reward:

            best_reward = episode_reward

        if (episode + 1) % 100 == 0:

            target_net.load_state_dict(
                online_net.state_dict()
            )

    runtime = (
        time.time()
        - start_time
    )
    torch.save(
        online_net.state_dict(),
        f"best_dqn_{network_name}_budget_{sensor_budget}_seed_{seed}.pth"
    )
    reward_df = pd.DataFrame({
        "Episode": range(1, len(reward_history) + 1),
        "Reward": reward_history
    })

    reward_df.to_csv(
        f"reward_history_{network_name}_budget_{sensor_budget}_seed_{seed}.csv",
        index=False
    )

    final_sensors = env.selected_nodes.copy()

    return (
        float(best_reward),
        float(reward_history[-1]),
        float(runtime),
        final_sensors,
    )