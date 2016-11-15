from cement.core import controller


class BaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = "Scripts/Tools used for working with automatic speech recognition."

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
