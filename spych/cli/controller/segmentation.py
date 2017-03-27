import os

from cement.core import controller

from spych.data import segmentation
from spych.assets import ctm


class ConvertSegmentsController(controller.CementBaseController):
    class Meta:
        label = 'convert-segments'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Convert the segments."

        arguments = [
            (['infile'], dict(action='store',
                              help='Path to input file.')),
            (['outfile'], dict(action='store',
                               help='Path to output file.')),
            (['--in-format'], dict(action='store',
                                   help='Input file format.',
                                   choices=['audacity', 'ctm'])),
            (['--out-format'], dict(action='store',
                                    help='Output file format.',
                                    choices=['audacity', 'ctm'])),
            (['--remove-labels'], dict(action='store',
                                       help='Path to input file.')),
            (['--replace'], dict(action='store',
                                 help='Replace things.',
                                 choices=['Jingle:Musik', 'Werbung:Sprache']))
        ]

    @controller.expose(hide=True)
    def default(self):
        inputfile_path = self.app.pargs.infile
        outfile_path = self.app.pargs.outfile

        in_format = self.app.pargs.in_format
        out_format = self.app.pargs.out_format

        if in_format == 'audacity':
            in_segmentations = [segmentation.Segmentation.from_audacity(inputfile_path)]
        elif in_format == 'ctm':
            in_segmentations = segmentation.Segmentation.from_ctm(inputfile_path)

        if out_format == 'audacity':
            if len(in_segmentations) > 1:
                if not os.path.isdir(outfile_path):
                    print('When there are multiple input segmentations, a directory has to be provided for audacity export.')
                else:
                    for seg in in_segmentations:
                        seg_path = os.path.join(outfile_path, '{}.txt'.format(seg.utterance_idx))
                        seg.to_audacity(seg_path)
            else:
                seg = in_segmentations[0]
                if os.path.isdir(outfile_path):
                    seg_path = os.path.join(outfile_path, '{}.txt'.format(seg.utterance_idx))
                else:
                    seg_path = outfile_path

                seg.to_audacity(seg_path)
        elif out_format == 'ctm':
            ctm_segments = []

            for seg in in_segmentations:
                for segment in seg.segments:
                    ctm_segments.append([seg.utterance_idx, segment.start, segment.end - segment.start, segment.value])

            ctm.write_file(outfile_path, ctm_segments)
