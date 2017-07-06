class ProcessingStage(object):
    def __init__(self, processing_function=None):
        self.processing_function = processing_function

    def process(self, feature_matrix):
        """ Process and return the given input features. """
        if self.processing_function is not None:
            return self.processing_function(feature_matrix)
        else:
            raise NotImplementedError("Process function of stage not implemented.")


class ExtractionStage(object):
    def __init__(self, extraction_function=None):
        self.extraction_function = extraction_function

    def extract(self, samples, sampling_rate):
        """ Extract features from given samples and return the features. """
        if self.extraction_function is not None:
            return self.extraction_function()
        else:
            raise NotImplementedError("Extraction function of stage not implemented.")


class FeaturePipeline(object):
    def __init__(self, stages=[], extract_stage=None):
        self.extract_stage = extract_stage
        self.stages = stages

    def process_signal(self, samples, sampling_rate, return_intermediate=False):
        """ Process the given signal. """

        if self.extract_stage is None:
            raise ValueError("No extraction stage given.")

        intermediate = []

        output = self.extract_stage.extract(samples, sampling_rate)

        if return_intermediate:
            intermediate.append(output)

        output = self.process(output, return_intermediate=return_intermediate)

        if return_intermediate:
            intermediate.extend(output)
            return intermediate
        else:
            return output

    def process(self, feature_matrix, return_intermediate=False):
        """
        Process the given features matrix N x [n] with N equals the number of frames.

        :param feature_matrix: Input data
        :param return_intermediate: If intermediate results should be returned.
        :return: N x [] output matrix, or if intermediate is True, a list of N x [] matrices (for every stage).
        """

        intermediate = []
        output = feature_matrix

        for stage in self.stages:
            output = stage.process(output)

            if return_intermediate:
                intermediate.append(output)

        if return_intermediate:
            return intermediate
        else:
            return output
