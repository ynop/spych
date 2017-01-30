class Alignment(object):
    """
    Represents the aligned items of two sequences.

    pairs e.g.:
    [
        (ref_item, hyp_item),   # Correct
        (ref_item1, hyp_item2), # Substitution
        (ref_item1, None),      # Deletion
        (None, hyp_item2),      # Insertion
        (ref_item1, hyp_item1)  # Correct
    ]
    """

    def __init__(self, reference_sequence, hypothesis_sequence, pairs):
        self.reference_sequence = reference_sequence
        self.hypothesis_sequence = hypothesis_sequence

        self.pairs = list(pairs)


class Aligner(object):
    """
    Create alignment between reference and hypothesis sequence. Trying to assign each item in the reference sequence an item from the hypothesis sequence.
    """

    def __init__(self):
        pass

    def align(self, reference, hypothesis):
        """
        Align two sequences.

        :param reference: Reference sequence
        :param hypothesis: Hypothesis sequence
        :return: Alignment
        """
        pass


class TimeBasedAligner(Aligner):
    """
    Creates aligned pairs of sequence items, when the items have start time and duration.
    """
    def __init__(self, start_time_threshold=1.0):
        self.start_time_threshold = start_time_threshold

    def align(self, reference, hypothesis):
        already_processed_hyp_items = set()
        pairs = []

        for ref_item in reference.items:
            matching_hyp_item = hypothesis.item_with_the_nearest_start_time(ref_item.start, label=ref_item.label, max_delta=self.start_time_threshold)

            if matching_hyp_item is not None and matching_hyp_item not in already_processed_hyp_items:
                already_processed_hyp_items.add(matching_hyp_item)
                pairs.append((ref_item, matching_hyp_item))
            else:
                pairs.append((ref_item, None))

        for hyp_item in hypothesis.items:
            if hyp_item not in already_processed_hyp_items:
                pairs.append((None, hyp_item))

        return Alignment(reference, hypothesis, pairs)
