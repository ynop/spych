import os

from cement.core import controller

from spych.scoring import align
from spych.scoring import evaluation
from spych.scoring import score
from spych.scoring import sequence


class ScoreController(controller.CementBaseController):
    class Meta:
        label = 'score'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Calculate score for hypotheses with given references."

        arguments = [
            (['reference'], dict(action='store', help='Path and type of the reference file. (types: ctm, audacity) (e.g. ref.ctm,ctm)')),
            (['hypothesis'], dict(action='store', help='Path and type of the hypothesis file. (types: ctm, audacity) (e.g. hyp.ctm,ctm)')),
            (['--align'],
             dict(action='store', help='How the sequences are aligned. (default time-based)', choices=['time-based'], default='time-based'))
        ]

    @controller.expose(hide=True)
    def default(self):
        reference = self.app.pargs.reference.split(',')
        hypothesis = self.app.pargs.hypothesis.split(',')
        aligner_name = self.app.pargs.align

        if len(reference) != 2:
            print('Invalid reference value. Must be of the form "path,type".')
            return

        if len(hypothesis) != 2:
            print('Invalid hypothesis value. Must be of the form "path,type".')
            return

        aligner = align.TimeBasedAligner()
        evaluator = evaluation.Evaluator()

        scorer = score.Scorer(aligner, evaluator)

        ref_path = reference[0]
        ref_type = reference[1]

        hyp_path = hypothesis[0]
        hyp_type = hypothesis[1]

        ref_seqs = self.load_sequences(ref_path, ref_type)
        hyp_seqs = self.load_sequences(hyp_path, hyp_type)

        result = scorer.score_list_of_sequences(ref_seqs, hyp_seqs)

        data = {
            'ref_path': ref_path,
            'hyp_path': hyp_path,
            'wer': result.error_rate,
            'n': result.num_total,
            'c': result.num_correct,
            's': result.num_substitutions,
            'd': result.num_deletions,
            'i': result.num_insertions,
        }

        self.app.render(data, 'score_base.mustache')

    def load_sequences(self, path, type):
        if type == 'ctm':
            return sequence.Sequence.from_ctm(path)
        elif type == 'audacity':
            return {"1": sequence.Sequence.from_audacity_labels(path)}
