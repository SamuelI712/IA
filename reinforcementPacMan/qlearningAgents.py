# qlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from game import *
from learningAgents import ReinforcementAgent
from featureExtractors import *

import random,util,math

class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - computeValueFromQValues
        - computeActionFromQValues
        - getQValue
        - getAction
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
    """
    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)
        
        states = []
        "*** YOUR CODE HERE ***"
        # keep a Counter/Dictionary of Q-values
        self.qvalues = util.Counter()
        
    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        # return the stored Q-value associated with the state and action
        return self.qvalues[(state, action)]


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        "*** YOUR CODE HERE ***"
        legalActions = self.getLegalActions(state)
        # if there are no legal actions, this is a terminal state and it's value should be 0
        if not legalActions:
            return 0.0
        else:
            # else, check for every action if it has a higher Q-value than the current highest Q-value
            # if so, set that as the current highest Q-value
            max = -99999
            for action in legalActions:
                qvalue = self.getQValue(state, action)
                if qvalue > max:
                    max = qvalue
            return max

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        legalActions = self.getLegalActions(state)
        # if there are no legal actions, this is a terminal state and it should return None
        if not legalActions:
            return None
        else:
            # else, check for every action if it has a higher Q-value than the current best action
            # if so, set that as the current best action
            bestAction = 'none', -99999
            for action in legalActions:
                qvalue = self.getQValue(state, action)
                if qvalue > bestAction[1]:
                    bestAction = action, qvalue
            return bestAction[0]

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        legalActions = self.getLegalActions(state)
        
        "*** YOUR CODE HERE ***"
        # there is a chance epsilon with which a random legal action gets chosen, otherwise, choose the best action
        if(util.flipCoin(self.epsilon)):
            return random.choice(legalActions)
        else:
            return self.computeActionFromQValues(state)

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        # get the legal actions of the next state
        nextLegalActions = self.getLegalActions(nextState)

        # get the highest Q-value of the next state with every of its legal actions
        nextMax = -99999
        for nextAction in nextLegalActions:
            nextQvalue = self.qvalues[(nextState, nextAction)]
            if nextQvalue > nextMax:
                nextMax = nextQvalue

        # if there are no legal actions, the (highest) Q-value should be 0
        if not nextLegalActions:
            nextMax = 0
                
        # calculate the sample
        sample = reward + self.discount * nextMax
        # and update the Q-value of the current state + action
        self.qvalues[(state, action)] = self.qvalues[(state, action)] + self.alpha * (sample - self.qvalues[(state, action)])

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, epsilon=0.05,gamma=0.8,alpha=0.2, numTraining=0, **args):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.getAction(self,state)
        self.doAction(state,action)
        return action


class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """
    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        "*** YOUR CODE HERE ***"
        value = 0
        features = self.featExtractor.getFeatures(state, action)

        # for every feature, multiply the value of the feature by its weight, and add that to 'value'
        for featureKey in features:
           
            featureValue = features[featureKey]
            featureWeight = self.weights[featureKey]
            value += featureWeight * featureValue

        return value

    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        "*** YOUR CODE HERE ***"
        nextLegalActions = self.getLegalActions(nextState)
        
        #Pega o maior Qvalue
        nextMax = -99999
        for nextAction in nextLegalActions:
            nextQvalue = self.getQValue(nextState, nextAction)
            if nextQvalue > nextMax:
                nextMax = nextQvalue

        if not nextLegalActions:
            nextMax = 0

        difference = (reward + self.discount * nextMax) - self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)

        # atualiza o valor de feature
        for featureKey in features:
            
            featureValue = features[featureKey]
            self.weights[featureKey] = self.weights[featureKey] + self.alpha * difference * featureValue

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"
            pass
