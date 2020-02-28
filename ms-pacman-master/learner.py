# -*- coding: utf-8 -*-

import os
import pickle
import random
from transition_model import get_next_state
from game_map_objects import GameMapObjects


class Learner(object):

    WEIGHTS_FILE = "weights.p"
    GLIE_FILE = "glie.p"

    def __init__(self, alpha=0.01, gamma=0.7):
        if not os.path.isfile(self.WEIGHTS_FILE):
            self.weights = [1] * 30
        else:
            self.weights = pickle.load(open(self.WEIGHTS_FILE, "rb"))
        if not os.path.isfile(self.GLIE_FILE):
            self.glie = 0.25
        else:
            self.glie = pickle.load(open(self.GLIE_FILE, "rb"))

        self.weights[self._to_weight_index(12)] = -100
        self.weights[self._to_weight_index(37)] = 200
        self.weights[self._to_weight_index(62)] = 10
        self.weights[self._to_weight_index(87)] = 50
        self.weights[self._to_weight_index(112)] = 200

        self.alpha = alpha
        self.gamma = gamma

    def _get_utility(self, state):
        state_rewards = self._get_state(state)
        utility = 0
        for i in range(len(state_rewards)):
            w_index = self._to_weight_index(i)
            utility += self.weights[w_index] * state_rewards[i]
        return utility

    def get_optimal_action(self, game):
        optimal_utility = float("-inf")
        optimal_actions = [0]  # noop.
        available_actions = game.available_actions()

        if random.random() <= self.glie:
            available_actions = [random.choice(available_actions)]

        for a in available_actions:
            next_state = get_next_state(game, a)
            utility = self._get_utility(next_state)
            if utility > optimal_utility:
                optimal_utility = utility
                optimal_actions = [a]
            elif utility == optimal_utility:
                optimal_actions.append(a)

        return (random.choice(optimal_actions), optimal_utility)

    def update_weights(self, prev_state, action, game, guess_utility, reward):
        self.glie = max(0.001, self.glie - 1e-5)
        curr_state = game.sliced_map.map.copy()
        curr_state[2, 2] = \
            prev_state[3, 2] if action == 2 else \
            prev_state[2, 1] if action == 3 else \
            prev_state[2, 3] if action == 4 else \
            prev_state[1, 2]

        state_rewards = self._get_state(curr_state)
        real_utility = reward + self.gamma * self.get_optimal_action(game)[1]
        error = 0.5 * (real_utility - guess_utility) ** 2

        print("Estimated utility: {}".format(guess_utility))
        print("Actual utility: {}".format(real_utility))
        print("Error: {}".format(error))

        for i in range(len(state_rewards)):
            if i in (12, 37, 62, 87, 112):
                continue
            self.weights[self._to_weight_index(i)] += \
                self.alpha * (real_utility - guess_utility) * \
                state_rewards[i] / self._to_weight_norm(i % 25)

    def _get_state(self, game_map):
        all_state = game_map.flatten()
        size = len(all_state)

        total_state = [0] * (5 * size)

        for i in range(size):
            classification = all_state[i]
            if classification == GameMapObjects.BAD_GHOST:
                total_state[i] = 1
            elif classification == GameMapObjects.GOOD_GHOST:
                total_state[i + size] = 1
            elif classification == GameMapObjects.PELLET:
                total_state[i + size * 2] = 1
            elif classification == GameMapObjects.POWER_UP:
                total_state[i + size * 3] = 1
            elif classification == GameMapObjects.FRUIT:
                total_state[i + size * 4] = 1

        return total_state

    def _to_weight_index(self, i):
        return self._to_weight_map(i % 25) + int(i / 25) * 6

    def _to_weight_map(self, i):
        return [
            0, 1, 2, 1, 0,
            1, 3, 4, 3, 1,
            2, 4, 5, 4, 2,
            1, 3, 4, 3, 1,
            0, 1, 2, 1, 0
        ][i]

    def _to_weight_norm(self, i):
        return [
            4, 8, 4, 8, 4,
            8, 4, 4, 4, 8,
            4, 4, 1, 4, 4,
            8, 4, 4, 4, 8,
            4, 8, 4, 8, 4
        ][i]

    def human_readable_weights(self):
        s = ""
        for i in range(5 * 25):
            s += "{:+05.2f} ".format(self.weights[self._to_weight_index(i)])
            if i % 5 == 4:
                s += "\n"
            if i % 25 == 24:
                s += "\n"
        return s

    def save(self):
        pickle.dump(self.weights, open(self.WEIGHTS_FILE, "wb"))
        pickle.dump(self.glie, open(self.GLIE_FILE, "wb"))
