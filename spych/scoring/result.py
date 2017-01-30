import collections


class LabelScore(object):
    """
    Represents the alignment stats of a single label.

    - Num correct occurences
    - Num substitutions per substituted hyp label
    - Num deletions
    - Num insertions
    """

    def __init__(self):
        self.correct = 0
        self.substitutions = collections.defaultdict(int)
        self.insertions = 0
        self.deletions = 0

    def merge_label_score(self, label_score):
        """ Merge the given label score into this one """
        self.correct += label_score.correct
        self.insertions += label_score.insertions
        self.deletions += label_score.deletions

        for label, count in label_score.substitutions.items():
            self.substitutions[label] += count

    @property
    def total(self):
        """ Return the number of labels in total """
        return self.correct + self.deletions + self.num_substitutions

    @property
    def num_substitutions(self):
        """ Return the number of substitutions """
        return sum(self.substitutions.values())


class Score(object):
    """
    Represents the score between of an alignment.
    """

    def __init__(self):
        self.labels = collections.defaultdict(LabelScore)

    def add_label_score(self, label, label_score):
        """ Merge the given label score into this score. """
        self.labels[label].merge_label_score(label_score)

    def merge_score(self, score):
        """ Merge the given score into this score. """
        for label, label_score in score.labels.items():
            self.add_label_score(label, label_score)

    @property
    def num_total(self):
        """ Return the number of labels in total """
        total = 0

        for label, label_score in self.labels.items():
            total += label_score.total

        return total

    @property
    def num_correct(self):
        """ Return the number of correct labels """
        correct_total = 0

        for label, label_score in self.labels.items():
            correct_total += label_score.correct

        return correct_total

    @property
    def num_deletions(self):
        """ Return the number of deletions """
        correct_deletions = 0

        for label, label_score in self.labels.items():
            correct_deletions += label_score.deletions

        return correct_deletions

    @property
    def num_insertions(self):
        """ Return the number of insertions """
        correct_insertions = 0

        for label, label_score in self.labels.items():
            correct_insertions += label_score.insertions

        return correct_insertions

    @property
    def num_substitutions(self):
        """ Return the number of substitutions """
        correct_substitutions = 0

        for label, label_score in self.labels.items():
            correct_substitutions += label_score.num_substitutions

        return correct_substitutions

    @property
    def error_rate(self):
        """ Return the error rate (D + I + S) / N """
        n = self.num_total

        if n == 0:
            return 0.0
        else:
            return (self.num_deletions + self.num_insertions + self.num_substitutions) / n

    @property
    def accuracy(self):
        """ Return the accuracy C / N """
        n = self.num_total

        if n == 0:
            return 0.0
        else:
            return self.num_correct / n

    @property
    def aggregated_label_stats(self):
        return self


class ScoreAggregation(object):
    """
    Represents a collection of scores. E.g every utterances results in a score, the aggregation represents the score over all utterances.

    Scores are stored as dict (key would then be the utterance id).

    """

    def __init__(self):
        self.scores = {}

    @property
    def num_total(self):
        """ Return the number of labels in total """
        total = 0

        for score in self.scores.values():
            total += score.num_total

        return total

    @property
    def num_correct(self):
        """ Return the number of correct labels """
        total = 0

        for score in self.scores.values():
            total += score.num_correct

        return total

    @property
    def num_deletions(self):
        """ Return the number of deletions """
        total = 0

        for score in self.scores.values():
            total += score.num_deletions

        return total

    @property
    def num_insertions(self):
        """ Return the number of insertions """
        total = 0

        for score in self.scores.values():
            total += score.num_insertions

        return total

    @property
    def num_substitutions(self):
        """ Return the number of substitutions """
        total = 0

        for score in self.scores.values():
            total += score.num_substitutions

        return total

    @property
    def error_rate(self):
        """ Return the error rate (D + I + S) / N """
        n = self.num_total

        if n == 0:
            return 0.0
        else:
            return (self.num_deletions + self.num_insertions + self.num_substitutions) / n

    @property
    def accuracy(self):
        """ Return the accuracy C / N """
        n = self.num_total

        if n == 0:
            return 0.0
        else:
            return self.num_correct / n

    @property
    def aggregated_label_stats(self):
        """ Get score representing all scores. """
        stats = Score()

        for score in self.scores.values():
            stats.merge_score(score)

        return stats

