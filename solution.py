import sys
import time
import itertools

from game_env import GameEnv
from game_state import GameState
"""
solution.py

This file is a template you should use to implement your solution.

You should implement each of the method stubs below. You may add additional methods and/or classes to this file if you 
wish. You may also create additional source files and import to this file if you wish.

COMP3702 Assignment 2 "CrystalRover" Support Code

Last updated by vp 09/09/2026
"""


class Solver:

    STUDENT_NAME = "Crystal Rover" # replace with your name
    STUDENT_ID = "12345678"  # replace with your student ID
    GITHUB_USERNAME = "cool-comp3702-student" # replace with your GitHub username

    def __init__(self, game_env: GameEnv):
        self.game_env = game_env
        #
        # TODO: Define any class instance variables you require (e.g. dictionary mapping state to VI value) here.
        #
        pass

    @staticmethod
    def testcases_to_attempt():
        """
        Return a list of testcase numbers you want your solution to be evaluated for.
        """
        # TODO: modify below if desired (e.g. disable larger testcases if you're having problems with RAM usage, etc)
        return [1, 2, 3, 4, 5]

    # === Value Iteration ==============================================================================================
   def get_valid_actions(self, state):
        """
        Get a list of valid actions from the given state.
        :param state: current GameState
        :return: list of valid action strings
        """
        valid_actions = []
        for action in self.ACTIONS:
            valid, error_msg, next_row, next_col = self.is_valid_action(state, action)
            if valid:
                valid_actions.append(action)
        return valid_actions
    

    def is_valid_action(self, state, action):
        """
        Check if the given action is valid from the given state.
        :param state: current GameState
        :param action: action string
        :return: True if valid, False otherwise
        """
        error_msg = None
        if action not in self.ACTIONS:
            error_msg = "Invalid action"
            return False, error_msg, None, None
        if action in self.JUMP_ACTIONS:
            if self.grid_data[state.row][state.col] != self.CRATER_TILE or state.rocket_jumps_left <= 0:
                error_msg = "Cannot perform rocket jump"
                return False, error_msg, None, None
            direction = self._action_direction(action)
            if direction == 'LEFT':
                delta_row, delta_col = 0, -1
            elif direction == 'RIGHT':
                delta_row, delta_col = 0, 1
            elif direction == 'UP':
                delta_row, delta_col = -1, 0
            elif direction == 'DOWN':
                delta_row, delta_col = 1, 0
            next_row = state.row + delta_row
            next_col = state.col + delta_col
            if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
                error_msg = "Cannot perform rocket jump: out of bounds"
                return False, error_msg, None, None
            if self.grid_data[next_row][next_col] == self.ROCK_TILE:
                error_msg = "Cannot perform rocket jump: rock in the way"
                return False, error_msg, None, None

        if action in self.BOOST_ACTIONS or action in self.WALK_ACTIONS:
            if self.grid_data[state.row][state.col] == self.CRATER_TILE:
                error_msg = "Cannot perform action: in a crater"
                return False, error_msg, None, None

            direction = self._action_direction(action)
            if direction == 'LEFT':
                delta_row, delta_col = 0, -1
            elif direction == 'RIGHT':
                delta_row, delta_col = 0, 1
            elif direction == 'UP':
                delta_row, delta_col = -1, 0
            elif direction == 'DOWN':
                delta_row, delta_col = 1, 0
            next_row = state.row + delta_row
            next_col = state.col + delta_col
            if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
                error_msg = "Cannot perform action: out of bounds"
                return False, error_msg, None, None
            if self.grid_data[next_row][next_col] == self.ROCK_TILE:
                error_msg = "Cannot perform action: rock in the way"
                return False, error_msg, None, None

            if action in self.BOOST_ACTIONS:
                # if it a boost action, check if you have fallen into a crater
                if self.grid_data[next_row][next_col] == self.CRATER_TILE:
                    return True, None, next_row, next_col

                next_row += delta_row
                next_col += delta_col
                if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
                    error_msg = "Cannot perform boost: out of bounds"
                    return False, error_msg, None, None
                if self.grid_data[next_row][next_col] == self.ROCK_TILE:
                    error_msg = "Cannot perform boost: rock in the way"
                    return False, error_msg, None, None
        
        return True, None, next_row, next_col
            
            
    def move(self, state, action, distance):
            """
            Apply the dynamics of the game to the given state and action and return the resulting state and reward.
            :param state: current GameState
            :param action: action string
            :return: action is valid (True/False), error message if invalid, next state, reward, state is terminal
            """
    
            if action not in self.ACTIONS:
                return False, "Invalid action", None, 0.0, None
    
            reward = -1 * self.ACTION_COST[action]
            next_row, next_col = state.row, state.col
    
            direction = self._action_direction(action)
    
            deltas = {
                'LEFT': (0, -1),
                'RIGHT': (0, 1),
                'UP': (-1, 0),
                'DOWN': (1, 0),
            }
    
            delta_row, delta_col = deltas[direction]
    
            if action in self.JUMP_ACTIONS:
                if self.grid_data[state.row][state.col] != self.CRATER_TILE:
                    return False, "Cannot perform rocket jump", None, 0.0, None
                move_distance = distance
            elif action in self.WALK_ACTIONS:
                if self.grid_data[state.row][state.col] == self.CRATER_TILE:
                    return False, "Cannot perform action: in a crater", None, 0.0, None
                move_distance = distance
            elif action in self.BOOST_ACTIONS:
                if self.grid_data[state.row][state.col] == self.CRATER_TILE:
                    return False, "Cannot perform action: in a crater", None, 0.0, None
                # sample the boost distance based on the boost probabilities
                move_distance = distance
    
            collision = False
            for _ in range(move_distance):
                candidate_row = next_row + delta_row
                candidate_col = next_col + delta_col
                if not (0 <= candidate_row < self.n_rows and 0 <= candidate_col < self.n_cols) \
                        or self.grid_data[candidate_row][candidate_col] == self.ROCK_TILE:
                    reward -= self.collision_penalty
                    collision = True
                    break
    
                next_row, next_col = candidate_row, candidate_col
    
                # fall into a crater
                if self.grid_data[next_row][next_col] == self.CRATER_TILE:
                    break
    
                # fall into lava
                if self.grid_data[next_row][next_col] == self.LAVA_TILE:
                    reward -= self.game_over_penalty
                    break
    
            crystal_status = state.crystal_status
            if (next_row, next_col) in self.crystal_positions:
                crystal_index = self.crystal_positions.index((next_row, next_col))
                if crystal_status[crystal_index] == 0:
                    crystal_status = list(crystal_status)
                    crystal_status[crystal_index] = 1
                    crystal_status = tuple(crystal_status)
    
            next_state = GameState(next_row, next_col, crystal_status)
            if not collision and self.is_game_over(next_state) and \
                    self.grid_data[next_row][next_col] != self.LAVA_TILE:
                reward -= self.game_over_penalty
    
            return True, None, next_state, reward, self.is_game_over(next_state)


    def get_transition_outcomes(self, state, action):
        env = self.environment
        pd, p2 = env.random_drift_prob, env.random_double_prob
        perp1, perp2 = env.PERPENDICULAR_ACTIONS[action]
        movement_distribution = [(action, 1 - pd), (perp1, pd / 2), (perp2, pd / 2)]
        double_distribution = [(1, 1 - p2), (2, p2)]

        if action in env.BOOST_ACTIONS:
            dist_options = list(enumerate(env.boost_probabilities))  # (distance, prob)
        else:
            dist_options = [(1, 1.0)]
        outcomes = {}
        for movement, prob_movement in movement_distribution:
            for double, prob_double in double_distribution:
                for dists in itertools.product(dist_options, repeat=int(double)):
                    current = state
                    prob = prob_movement * prob_double 
                    total_reward = 0.0
                    for distance, prob_distance in dists:
                        prob *= prob_distance
                        valid, error, outcome_state, reward, terminal = move(current, movement, distance)
                        if not valid:
                            continue
                        current = outcome_state
                        total_reward += reward
                        if terminal: 
                            break
                    key = (current, total_reward)
                    outcomes[key] = outcomes.get(key, 0.0) + prob
        return [(p, s, r) for (s, r), p in outcomes.items()]
                    
                    
                
                    
                        
                    
                    


        
    def vi_initialise(self):
        """
        Initialise any variables required before the start of Value Iteration.
        """
        env = self.environment
        start = env.get_init_state()
        visited = {start}
        froniter = [start]
        self.states = []
        self.valid_actions = {}    
        self.transitions = {}
        while frontier:
            s = frontier.pop()
            self.states.append(s)
            if env.is_solved(s) or env.is_game_over(s):
                self.valid_actions[s] = []
                continue
            actions = get_valid_actions(s):
            self.valid_actions[s] = actions
            for a in actions:
                outcomes = get_transition_outcomes(s, actions)
                self.transitions[(s, a)] = outcomes
                for p, s2 , r in outcomes:
                    if s2 not in visited:
                        visited.add(s2)
                        frontier.append(s2)
                        
                    
      
               
            

     

                        
        #
        # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
        #  perform value iteration in this method.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Value Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def vi_iteration(self):
        """
        Perform a single iteration of Value Iteration (i.e. loop over the state space once).
        """
        #
        # TODO: Implement code to perform a single iteration of Value Iteration here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def vi_plan_offline(self):
        """
        Plan using Value Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.vi_initialise()
        while True:
            self.vi_iteration()

            # NOTE: vi_iteration is always called before vi_is_converged
            if self.vi_is_converged():
                break

    def vi_get_state_value(self, state: GameState):
        """
        Retrieve V(s) for the given state.
        :param state: the current state
        :return: V(s)
        """
        #
        # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
        #  value for V(s) has not yet been computed, this function should return 0.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def vi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    # === Policy Iteration =============================================================================================

    def pi_initialise(self):
        """
        Initialise any variables required before the start of Policy Iteration.
        """
        #
        # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
        #  perform policy iteration in this method. You can assume an initial policy of always applying WALK_RIGHT.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_is_converged(self):
        """
        Check if Policy Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Policy Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_iteration(self):
        """
        Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
        policy improvement).
        """
        #
        # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_plan_offline(self):
        """
        Plan using Policy Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.pi_initialise()
        while True:
            self.pi_iteration()

            # NOTE: pi_iteration is always called before pi_is_converged
            if self.pi_is_converged():
                break

    def pi_select_action(self, state: GameState):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ACTIONS)
        """
        #
        # TODO: Implement code to return an action for the given state (based on your stored PI policy) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #

