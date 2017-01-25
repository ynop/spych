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


class Score(object):
    """
    Represents the score between of an alignment.
    """
    def __init__(self):
        self.labels = collections.defaultdict(LabelScore)


class Scorer(object):
    """
    Calculates the score between two aligned sequences.
    """
    def __init__(self):
        pass

    def score(self, alignment):
        """
        Calculate and return the score for the given alignment.
        """
        score = Score()

        for pair in alignment.pairs:
            ref = pair[0]
            hyp = pair[1]

            if ref is None and hyp is not None:
                score.labels[hyp.label].insertions += 1

            elif ref is not None and hyp is None:
                score.labels[ref.label].deletions += 1

            elif ref.label != hyp.label:
                score.labels[ref.label].substitutions[hyp.label] += 1

            elif ref.label == hyp.label:
                score.labels[ref.label].correct += 1

        return score
