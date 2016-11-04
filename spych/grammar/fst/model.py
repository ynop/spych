

class FiniteStateTransducer(object):

    def __init__(self):
        self.start = None
        self.final = None

        self.states = []
        self.arcs = []


class FSTState(object):

    def __init__(self, identifier=0, weight=0.0):
        self.identifier = identifier
        self.weight = weight

        self.inputs = []
        self.outputs = []


class FSTArc(object):

    def __init__(self, src_state, dest_state, label, weight=0.0):
        self.src_state = src_state
        self.dest_state = dest_state
        self.label = label
        self.weight = weight