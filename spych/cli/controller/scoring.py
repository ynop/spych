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
             dict(action='store', help='How the sequences are aligned. (default time-based)', choices=['time-based'], default='time-based')),
            (['--start-time-threshold'],
             dict(action='store', help='The delta start time in seconds to consider a hypothesis as a match. (default 1.0)', default=1.0))
        ]

    @controller.expose(hide=True)
    def default(self):
        reference = self.app.pargs.reference.split(',')
        hypothesis = self.app.pargs.hypothesis.split(',')
        aligner_name = self.app.pargs.align
        start_threshold = self.app.pargs.start_time_threshold

        if len(reference) != 2:
            print('Invalid reference value. Must be of the form "path,type".')
            return

        if len(hypothesis) != 2:
            print('Invalid hypothesis value. Must be of the form "path,type".')
            return

        aligner = align.TimeBasedAligner(start_time_threshold=start_threshold)
        evaluator = evaluation.Evaluator()

        scorer = score.Scorer(aligner, evaluator)

        ref_path = reference[0]
        ref_type = reference[1]

        hyp_path = hypothesis[0]
        hyp_type = hypothesis[1]

        ref_seqs = self.load_sequences(ref_path, ref_type)
        hyp_seqs = self.load_sequences(hyp_path, hyp_type)

        if len(ref_seqs) == 1 and len(hyp_seqs) == 1:
            result = scorer.score_sequences(list(ref_seqs.values())[0], list(hyp_seqs.values())[0])
        else:
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

        stats = result.aggregated_label_stats

        details = []

        for label in sorted(stats.labels.keys()):
            label_score = stats.labels[label]
            details.append({
                'value': '{:30s}'.format(label),
                'n': '{:<4d}'.format(label_score.total),
                'c': '{:<4d}'.format(label_score.correct),
                's': '{:<4d}'.format(label_score.num_substitutions),
                'd': '{:<4d}'.format(label_score.deletions),
                'i': '{:<4d}'.format(label_score.insertions)
            })

        data['words'] = details

        self.app.render(data, 'score_base.mustache')

    def load_sequences(self, path, type):
        if type == 'ctm':
            return sequence.Sequence.from_ctm(path)
        elif type == 'audacity':
            return {"1": sequence.Sequence.from_audacity_labels(path)}
