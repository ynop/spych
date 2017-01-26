from spych.scoring import result
from spych.scoring import sequence


class Scorer(object):
    """
    Creates alignment and evaluates score of the alignments.
    """

    def __init__(self, aligner, evaluator):
        self.aligner = aligner
        self.evaluator = evaluator

    def score_sequences(self, ref_sequence, hyp_sequence):
        """ Align and evaluate two sequences. """
        alignment = self.aligner.align(ref_sequence, hyp_sequence)
        score = self.evaluator.match(alignment)

        return score

    def score_list_of_sequences(self, ref_sequences, hyp_sequences):
        """ Align and evaluate sequences from two dictionaries. The keys in the dictionary represent the id to match two sequences from both dicts. """

        if set(ref_sequences.keys()) != set(hyp_sequences.keys()):
            print("Reference and hypothesis have different sequences. Only evaluate the matching ones.")

        score = result.ScoreAggregation()

        for seq_id, sequence in ref_sequences.items():
            if seq_id in hyp_sequences.keys():
                seq_score = self.score_sequences(sequence, hyp_sequences[seq_id])
                score.scores[seq_id] = seq_score

        return score

    def score_ctm(self, ref_ctm_path, hyp_ctm_path):
        """ Align and evaluate the sequences of two ctm files. """
        ref_sequences = sequence.Sequence.from_ctm(ref_ctm_path)
        hyp_sequences = sequence.Sequence.from_ctm(hyp_ctm_path)

        return self.score_list_of_sequences(ref_sequences, hyp_sequences)

    def score_audacity_labels(self, ref_audacity_label_path, hyp_audacity_label_path):
        """ Align and evaluate the two sequences from two audacity label files. """
        ref_sequence = sequence.Sequence.from_audacity_labels(ref_audacity_label_path)
        hyp_sequence = sequence.Sequence.from_audacity_labels(hyp_audacity_label_path)

        return self.score_sequences(ref_sequence, hyp_sequence)
