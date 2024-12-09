# src/continuous_learning.py

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import logging

logger = logging.getLogger(__name__)

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
    
    def push(self, transition):
        self.memory.append(transition)
    
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def __len__(self):
        return len(self.memory)

class DQN(nn.Module):
    def __init__(self, state_size, action_size, hidden_size=64):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, action_size)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)

class TradingAgent:
    def __init__(self, state_size, action_size, device='cpu', lr=1e-3, gamma=0.99, memory_capacity=10000, batch_size=64):
        self.state_size = state_size
        self.action_size = action_size
        self.device = device
        self.gamma = gamma
        self.batch_size = batch_size
        
        self.policy_net = DQN(state_size, action_size).to(device)
        self.target_net = DQN(state_size, action_size).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.memory = ReplayMemory(memory_capacity)
        self.steps_done = 0
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.loss_fn = nn.MSELoss()
    
    def select_action(self, state):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
        else:
            with torch.no_grad():
                state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state)
                return q_values.argmax().item()
    
    def optimize_model(self):
        if len(self.memory) < self.batch_size:
            return
        
        transitions = self.memory.sample(self.batch_size)
        batch = list(zip(*transitions))
        
        states = torch.FloatTensor(np.array(batch[0])).to(self.device)
        actions = torch.LongTensor(batch[1]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(batch[2]).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(np.array(batch[3])).to(self.device)
        dones = torch.FloatTensor(batch[4]).unsqueeze(1).to(self.device)
        
        current_q = self.policy_net(states).gather(1, actions)
        max_next_q = self.target_net(next_states).max(1)[0].unsqueeze(1)
        target_q = rewards + (self.gamma * max_next_q * (1 - dones))
        
        loss = self.loss_fn(current_q, target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def save_model(self, path):
        torch.save(self.policy_net.state_dict(), path)
    
    def load_model(self, path):
        self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict())


