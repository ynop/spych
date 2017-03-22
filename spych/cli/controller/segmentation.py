import os

from cement.core import controller

from spych.data import segmentation


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
            (['--informat'], dict(action='store',
                                  help='Input file format.',
                                  choices=['audacity', 'ctm'])),
            (['--outformat'], dict(action='store',
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
        print(self.app.pargs.informat)

        inputfile_path = self.app.pargs.infile
        outfile_path = self.app.pargs.outfile

        os.makedirs(outfile_path, exist_ok=True)

        segmentations = segmentation.Segmentation.from_ctm(inputfile_path)

        for seg in segmentations:
            output_filepath = os.path.join(outfile_path, '{}.txt'.format(seg.utterance_idx))
            seg.to_audacity(output_filepath)
