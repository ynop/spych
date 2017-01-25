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

    def align(self, reference, hypothesis):
        not_processed_hyp_items = list(range(len(hypothesis.items)))
        pairs = []

        for ref_item in reference.items:
            possible_match_items = hypothesis.items_in_interval(ref_item.start, ref_item.start + ref_item.duration)
            match_item = None

            if len(possible_match_items) > 0:
                match_index, match_item = self._find_best_matching_item_in_list(ref_item, possible_match_items)

                if match_item is not None:
                    not_processed_hyp_items.remove(match_index)

            pairs.append((ref_item, match_item))

        for i in not_processed_hyp_items:
            match_item = hypothesis.items[i]
            pairs.append((None, match_item))

        return Alignment(reference, hypothesis, pairs)

    def _find_best_matching_item_in_list(self, ref_item, possible_match_items):
        """
        Find the best matching item in a list of hyp items and return the index and the item.
        """
        best_item = possible_match_items[0][1]
        best_item_index = possible_match_items[0][0]
        best_item_start_difference = abs(ref_item.start - best_item.start)

        for i in range(1, len(possible_match_items)):
            hyp_item = possible_match_items[i][1]
            difference = abs(ref_item.start - hyp_item.start)

            has_better_difference = difference < best_item_start_difference
            best_matches_label = best_item.label == ref_item.label
            hyp_matches_label = hyp_item.label == ref_item.label

            if (hyp_matches_label and not best_matches_label) or (has_better_difference and not best_matches_label):
                best_item = hyp_item
                best_item_index = possible_match_items[i][0]
                best_item_start_difference = difference

        return best_item_index, best_item


