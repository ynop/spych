import numpy as np

from . import base


class LogStage(base.ProcessingStage):
    def process(self, feature_matrix):
        return np.log(np.maximum(1e-10, feature_matrix))


class ExponentialStage(base.ProcessingStage):
    def process(self, feature_matrix):
        output = np.exp(feature_matrix)
        output[output == np.inf] = np.finfo(output.dtype).max
        return output


class RescalingStage(base.ProcessingStage):
    def __init__(self, target_min=0.0, target_max=1.0, reference_min=None, reference_max=None):
        self.reference_min = reference_min
        self.reference_max = reference_max

        self.target_min = target_min
        self.target_max = target_max

    def process(self, feature_matrix):
        min = self.reference_min
        max = self.reference_max

        if min is None or max is None:
            min, max = self._calculate_min_max()

        output = (feature_matrix - min) / (max - min)
        output = (output * (self.target_max - self.target_min)) + self.target_min

        return output

    def _calculate_min_max(self, feature_matrix):
        return np.min(feature_matrix), np.max(feature_matrix)
