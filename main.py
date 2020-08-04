from optionsbacktrader import OptionsBroker, OptionsTradingEnvironment
from stable_baselines3 import PPO

broker = OptionsBroker()
broker.load_historical_data('./Sample_SPX_20151001_to_20151030.sqlite3', fidelity='day')

env = OptionsTradingEnvironment(broker)

policy_kwargs = dict(net_arch=[1024, 768, 512, 256])
model = PPO('MlpPolicy',
            env,
            verbose=1,
            n_steps=len(broker.get_trading_days()),
            policy_kwargs=policy_kwargs,
            tensorboard_log='./ppo_tensorboard')
model.learn(total_timesteps=100)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
        break

print('DONE')

env.close()
