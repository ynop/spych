from cement.core import controller

from spych.pronunciation import lexicon


class LexiconController(controller.CementBaseController):
    class Meta:
        label = 'lexicon'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Working with lexicon."

        arguments = [
            (['path'], dict(action='store', help='path to the lexicon.'))
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()

    @controller.expose(help="Print information about a given lexicon.")
    def info(self):
        lex = lexicon.Lexicon.load_from_file(self.app.pargs.path)

        info_data = {
            "path": self.app.pargs.path,
            "num_words": lex.get_number_of_entries(count_all=False),
            "num_prons": lex.get_number_of_entries(count_all=True)
        }

        self.app.render(info_data, 'lexicon_info.mustache')
