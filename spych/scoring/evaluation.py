from spych.scoring import result


class Evaluator(object):
    """
    Calculates the score between two aligned sequences.
    """

    def __init__(self):
        pass

    def match(self, alignment):
        """
        Calculate and return the score for the given alignment.
        """
        score = result.Score()

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