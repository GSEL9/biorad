# -*- coding: utf-8 -*-
#
# classifiers.py
#

"""
"""

__author__ = 'Severin Langberg'
__email__ = 'langberg91@gmail.com'

from . import base

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.cross_decomposition import PLSRegression

from smac.configspace import ConfigurationSpace
from ConfigSpace.conditions import InCondition
from ConfigSpace.hyperparameters import CategoricalHyperparameter
from ConfigSpace.hyperparameters import UniformFloatHyperparameter
from ConfigSpace.hyperparameters import UniformIntegerHyperparameter


SEED = 0


class RFEstimator(base.BaseEstimator):

    NAME = 'RFEstimator'

    def __init__(
        self,
        mode='classification',
        model=RandomForestClassifier(
            n_jobs=-1,
            verbose=False,
            oob_score=False,
            min_samples_split=2,
            class_weight='balanced',
        )
    ):

        super().__init__(model=model, mode=mode)

    @property
    def hparam_space(self):
        """Returns the PLS Regression hyperparameter space."""

        # NOTE: This algorithm is stochastic and its performance varies
        # across random states.
        hparam_space = (
            UniformIntegerHyperparameter(
                '{}__random_state'.format(self.NAME), lower=0, upper=1000,
            ),
            UniformIntegerHyperparameter(
                '{}__n_estimators'.format(self.NAME),
                lower=10,
                upper=3000,
                default_value=100
            ),
            CategoricalHyperparameter(
                '{}__criterion'.format(self.NAME),
                ['gini', 'entropy'], default_value='gini'
            ),
            CategoricalHyperparameter(
                '{}__max_depth'.format(self.NAME),
                [3, 5, None], default_value=None
            ),
            CategoricalHyperparameter(
                '{}__max_features'.format(self.NAME),
                ['auto', 'sqrt', 'log2', None], default_value=None
            ),
            CategoricalHyperparameter(
                '{}__bootstrap'.format(self.NAME),
                [True, False], default_value=True
            ),
            UniformFloatHyperparameter(
                '{}__min_samples_leaf'.format(self.NAME),
                lower=1.5,
                upper=50.5,
                default_value=1.0
            ),
        )
        return hparam_space


class PLSREstimator(base.BaseEstimator):

    NAME = 'PLSREstimator'

    def __init__(
        self,
        mode='classification',
        model=PLSRegression(scale=False, copy=True, max_iter=-1)
    ):

        super().__init__(model=model, mode=mode)

    @property
    def config_space(self):
        """Returns the PLS regression hyperparameter configuration space."""

        global SEED

        tol = UniformFloatHyperparameter(
            'tol', lower=1e-9, upper=1e-3, default_value=1e-7
        )
        n_components = UniformIntegerHyperparameter(
            'n_components', lower=1, upper=40, default_value=27
        )
        # Add hyperparameters to config space.
        config = ConfigurationSpace()
        config.seed(SEED)
        config.add_hyperparameters((tol, n_components))

        return config


# * The n_jobs > 1 does not have any effect when solver
#   is set to 'liblinear'.
# * Should explicitly specify penalty since this param depends
#   on the selected solver. Using L1 enables dim reduction in high
#   dim classification problems.
# * The `liblinear` solver allows for binary classification with L1 and L2
#   regularization, is robust to unscaled data sets, penalize the intercept
#   term, but is not faster for larger data sets.
# * Dual formulation is only implemented for l2 penalty with liblinear
#   solver. Thus, enabling to select from l1 or l2 requires Dual=False.
# * Set multi class to `ovr` for binary problems.
# * The max_iter is not usefull with `liblinear` solver.
class LogRegEstimator(base.BaseEstimator):

    NAME = 'LogRegEstimator'

    def __init__(
        self,
        mode='classification',
        model=LogisticRegression(
            solver='liblinear',
            max_iter=1000,
            verbose=0,
            n_jobs=1,
            dual=False,
            multi_class='ovr',
            warm_start=False,
            class_weight='balanced',
        )
    ):

        super().__init__(model=model, mode=mode)

    @property
    def config_space(self):
        """Returns the LR hyperparameter configuration space."""

        global SEED

        random_states = UniformIntegerHyperparameter(
            'random_state', lower=0, upper=1000,
        )
        C = UniformFloatHyperparameter(
            'C', lower=0.001, upper=1000.0, default_value=1.0
        )
        penalty = CategoricalHyperparameter(
            'penalty', ['l1', 'l2'], default_value='l2'
        )
        # Add hyperparameters to config space.
        config = ConfigurationSpace()
        config.seed(SEED)
        config.add_hyperparameters((random_states, C, penalty))

        return config


class SVCEstimator(base.BaseEstimator):

    NAME = 'SVCEstimator'

    def __init__(
        self,
        mode='classification',
        model=SVC(
            class_weight='balanced',
            verbose=False,
            cache_size=500,
            max_iter=-1,
            decision_function_shape='ovr',
        )
    ):

        super().__init__(model=model, mode=mode)

    @property
    def config_space(self):
        """Returns the SVC hyperparameter configuration space."""

        global SEED

        random_states = UniformIntegerHyperparameter(
            'random_state', lower=0, upper=1000,
        )
        C = UniformFloatHyperparameter(
            'C', lower=0.001, upper=1000.0, default_value=1.0
        )
        shrinking = CategoricalHyperparameter(
            'shrinking', [True, False], default_value=True
            #['true', 'false'], default_value='true'
        )
        kernel = CategoricalHyperparameter(
            'kernel', ['linear', 'rbf', 'poly', 'sigmoid'],
        )
        gamma = CategoricalHyperparameter(
            'gamma', ['auto', 'value'], default_value='auto'
        )
        gamma_value = UniformFloatHyperparameter(
            'gamma_value', lower=0.0001, upper=8, default_value=1
        )
        degree = UniformIntegerHyperparameter(
            'degree', lower=1, upper=5, default_value=3
        )
        coef0 = UniformFloatHyperparameter(
            'coef0', lower=0.0, upper=10.0, default_value=0.0
        )
        # Add hyperparameters to config space.
        config = ConfigurationSpace()
        config.seed(SEED)
        config.add_hyperparameters(
            (
                random_states,
                C,
                shrinking,
                kernel,
                degree,
                coef0,
                gamma,
                gamma_value
            )
        )
        # Conditionals on hyperparameters specific to kernels.
        config.add_conditions(
            (
                InCondition(child=degree, parent=kernel, values=['poly']),
                InCondition(child=gamma_value, parent=gamma, values=['value']),
                InCondition(
                    child=coef0, parent=kernel,
                    values=['poly', 'sigmoid']
                ),
                InCondition(
                    child=gamma, parent=kernel,
                    values=['rbf', 'poly', 'sigmoid']
                )
            )
        )
        return config


# NOTE: This algorithm does not associate hyperparameters.
class GNBEstimator(base.BaseEstimator):

    NAME = 'GNBEstimator'

    def __init__(
        self,
        mode='classification',
        model=GaussianNB()
    ):

        super().__init__(model=model, mode=mode)


class KNNEstimator(base.BaseEstimator):

    NAME = 'KNNEstimator'

    def __init__(
        self,
        mode='classification',
        model=KNeighborsClassifier(algorithm='auto')
    ):

        super().__init__(model=model, mode=mode)

    @property
    def config_space(self):
        """Returns the KNN hyperparameter configuration space."""

        global SEED

        n_neighbors = UniformIntegerHyperparameter(
            'n_neighbors', 3, 100, default_value=5
        )
        leaf_size = UniformIntegerHyperparameter(
            'leaf_size', 10, 100, default_value=30
        )
        metric = CategoricalHyperparameter(
            'metric',
            ['euclidean', 'manhattan', 'chebyshev', 'minkowski'],
            default_value='minkowski'
        )
        p = UniformIntegerHyperparameter('p', 1, 5, default_value=2)

        # Add hyperparameters to config space.
        config = ConfigurationSpace()
        config.seed(SEED)
        config.add_hyperparameters((n_neighbors, leaf_size, metric, p))

        # Conditionals on hyperparameters specific to kernels.
        config.add_condition(
            InCondition(child=p, parent=metric, values=['minkowski'])
        )
        return config


if __name__ == '__main__':
    pass
