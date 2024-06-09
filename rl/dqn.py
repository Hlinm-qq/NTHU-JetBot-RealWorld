import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class DeepQNetwork():
    def __init__(
        self,
        n_actions,
        input_shape,
        qnet,
        device,
        learning_rate = 2e-4,
        reward_decay = 0.99,
        replace_target_iter = 1000,
        memory_size = 10000,
        batch_size = 32,
    ):
        # initialize parameters
        self.n_actions = n_actions
        self.input_shape = input_shape
        self.lr = learning_rate
        self.gamma = reward_decay
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.device = device
        self.learn_step_counter = 0
        self.init_memory()

        # Network
        self.qnet_eval = qnet(self.input_shape, self.n_actions).to(self.device)
        self.qnet_target = qnet(self.input_shape, self.n_actions).to(self.device)
        self.qnet_target.eval()
        self.optimizer = optim.RMSprop(self.qnet_eval.parameters(), lr=self.lr)

    def choose_action(self, state, epsilon=0):
        s = {}
        for key in state:
            s[key] = torch.FloatTensor(np.expand_dims(state[key],0)).to(self.device)
        with torch.no_grad():
            actions_value = self.qnet_eval.forward(s)
        if np.random.uniform() > epsilon:   # greedy
            action = torch.max(actions_value, 1)[1].data.cpu().numpy()[0]
        else:   # random
            action = np.random.randint(0, self.n_actions)
        return action

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.qnet_target.load_state_dict(self.qnet_eval.state_dict())

        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_counter, size=self.batch_size)

        b_s, b_s_ = {}, {}
        for key in self.memory["s"]:
            b_s[key] = torch.FloatTensor(self.memory["s"][key][sample_index]).to(self.device)
        b_a = torch.LongTensor(self.memory["a"][sample_index]).to(self.device)
        b_r = torch.FloatTensor(self.memory["r"][sample_index]).to(self.device)
        for key in self.memory["s_"]:
            b_s_[key] = torch.FloatTensor(self.memory["s_"][key][sample_index]).to(self.device)
        b_d = torch.FloatTensor(self.memory["done"][sample_index]).to(self.device)

        q_curr_eval = self.qnet_eval(b_s).gather(1, b_a)
        q_next_target = self.qnet_target(b_s_).detach()

        next_state_values = q_next_target.max(1)[0].view(-1, 1)   # DQN
        # q_next_eval = self.qnet_eval(b_s_).detach()
        # next_state_values = q_next_target.gather(1, q_next_eval.max(1)[1].unsqueeze(1))   # DDQN

        q_curr_recur = b_r + (1-b_d) * self.gamma * next_state_values
        self.loss = F.smooth_l1_loss(q_curr_eval, q_curr_recur)

        self.optimizer.zero_grad()
        self.loss.backward()
        self.optimizer.step()
        self.learn_step_counter += 1
        return self.loss.detach().cpu().numpy()

    def init_memory(self):
        self.memory = {
            "s": {},
            "a": np.zeros((self.memory_size, 1)),
            "r": np.zeros((self.memory_size, 1)),
            "s_": {},
            "done": np.zeros((self.memory_size, 1)),
        }

    def store_transition(self, s, a, r, s_, d):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0
        if self.memory_counter <= self.memory_size:
            index = self.memory_counter % self.memory_size
        else:
            index = np.random.randint(self.memory_size)
        for key in s:
            if key not in self.memory["s"]:
                self.memory["s"][key] = np.zeros((self.memory_size, *self.input_shape))
            self.memory["s"][key][index] = s[key]
        self.memory["a"][index] = np.array(a).reshape(-1,1)
        self.memory["r"][index] = np.array(r).reshape(-1,1)
        for key in s_:
            if key not in self.memory["s_"]:
                self.memory["s_"][key] = np.zeros((self.memory_size, *self.input_shape))
            self.memory["s_"][key][index] = s_[key]
        self.memory["done"][index] = np.array(d).reshape(-1,1)
        self.memory_counter += 1
    
    def save_load_model(self, op, total_step=0, episode=0, path="save", fname="qnet.pt"):
        import os
        if not os.path.exists(path):
            os.makedirs(path)
        file_path = os.path.join(path, fname)
        if op == "save":
            torch.save({
                "total_step": total_step,
                "episode": episode,
                "qnet": self.qnet_eval.state_dict()
            }, file_path)
        elif op == "load":
            state_dict = torch.load(file_path, map_location=self.device)
            # self.qnet_eval.load_state_dict(state_dict["qnet"])
            # self.qnet_target.load_state_dict(state_dict["qnet"])
            # return state_dict["total_step"], state_dict["episode"]
            self.qnet_eval.load_state_dict(state_dict)
            self.qnet_target.load_state_dict(state_dict)
            return state_dict, state_dict