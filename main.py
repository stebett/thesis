import os
import numpy as np
from nest import set_verbosity

from agent.ddpg import DDPGAgent
from env.neur_env import Neuron_env
from utils.utils import Recorder, take_checkpoint


checkpoint_path = 'checkpoints/'
set_verbosity(30)

episodes = 50000
batch_size = 2
fixed = ['neuron']

tau = 1e-3
buffer_maxlen = 100000
critic_lr = 1e-3
actor_lr = 1e-4

env = Neuron_env(fixed)
recorder = Recorder(['action_{}'.format(n) for n in range(len(env.mutable_params))])
agent = DDPGAgent(env, tau, buffer_maxlen, critic_lr, actor_lr)
if os.path.isfile(checkpoint_path + 'model.pth.tar'):
    agent.load_checkpoint(checkpoint_path + 'model.pth.tar')

for episode in range(episodes + 1):

    state = env.reset()
    action = agent.get_action(state)
    reward, next_state = env.step(action)
    
    agent.replay_buffer.push(state, action, reward)
    q_loss, policy_loss = agent.update(batch_size)

    params = env.mutable_params
    recorder.push(episode, reward, *next_state, q_loss, policy_loss, *params)

    print('Episode ' + str(episode), end='\r')

    if episode % 490 == 0:
        agent.test = True
    if episode % 3 == 0:
        agent.test = False
        take_checkpoint(agent, recorder, checkpoint_path)

