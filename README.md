Rabbits powered by Tensorflow neural networks run around the screen, drink from water sources, eat from food sources, and hide from enemy foxes.

View my RabbitSimulator project repository for the original project

Required packages: Tensorflow, Pygame
How to run: 
- You can run the neural network trainer by running the training_classes/Training.py file. (takes a LONG time, run overnight or in the background)
- You can run the simulation by running the game_classes/Game.py file.

General Info:
- When training is complete, the neural network weights are saved to the game_classes folder. The saved weights are automatically loaded when the simulation is run.
- Rabbits do not mate in this version. The rabbits are programmed to reproduce after they eat 2 times and/or drink 2 times.
- Simulation ends when all the rabbits die or the rabbit population exceeds 400.

