import operator

from collections import deque

from spych.grammar import model
from spych.grammar.fst import model as fst_model


class FSTPart:
    def __init__(self):
        self.input_arcs = []
        self.output_arcs = []

        self.is_optional = False


class FSTSerializer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.rule_parts = {}

    def serialize(self):
        part = self.__create_part_from_rule(self.grammar.root_rule)
        fst = self.__create_fst_from_part(part)

        # set label ids
        labels = {}
        i = 1

        for arc in fst.arcs:
            if not arc.label in labels.keys():
                labels[arc.label] = i
                i += 1

        # FST
        lines = []

        for arc in fst.arcs:
            lines.append("{} {} {} {} {}".format(arc.src_state.identifier, arc.dest_state.identifier, arc.label, arc.label, arc.weight))

        lines.append("{} 1.0".format(fst.final.identifier))
        lines.append("")

        fst_string = "\n".join(lines)

        # LABEL
        lines = []

        lines.append("<eps> 0")

        for label, index in sorted(labels.items(), key=operator.itemgetter(1)):
            lines.append("{} {}".format(label, index))

        lines.append("")

        label_string = "\n".join(lines)

        return fst_string, label_string

    def __create_fst_from_part(self, part):
        fst = fst_model.FiniteStateTransducer()

        start = fst_model.FSTState(0)

        for input_arc in part.input_arcs:
            input_arc.src_state = start
            start.outputs.append(input_arc)

        end = fst_model.FSTState(1)

        for output_arc in part.output_arcs:
            output_arc.dest_state = end
            end.inputs.append(output_arc)

        # set state ids
        q = deque([start])
        marked = set()
        i = 0

        while len(q) > 0:
            current_state = q.popleft()
            current_state.identifier = i
            i += 1

            fst.states.append(current_state)

            weight = 1.0

            if len(current_state.outputs) > 0:
                weight = 1.0 / len(current_state.outputs)

            for output_arc in current_state.outputs:
                dest_state = output_arc.dest_state
                output_arc.weight = weight

                fst.arcs.append(output_arc)

                if not dest_state in marked:
                    marked.add(dest_state)
                    q.append(dest_state)

        fst.start = start
        fst.final = end

        return fst

    def __create_part_from_rule(self, rule):
        return self.__create_part_from_element(rule.value)

    def __create_part_from_element(self, element):
        part = None

        if isinstance(element, model.Token):
            part = self.__create_part_from_token(element)
        elif isinstance(element, model.RuleReference):
            part = self.__create_part_from_rule_reference(element)
        elif isinstance(element, model.Group):
            part = self.__create_part_from_group(element)
        elif isinstance(element, model.OptionalGroup):
            part = self.__create_part_from_optional_group(element)
        elif isinstance(element, model.Sequence):
            part = self.__create_part_from_sequence(element)
        elif isinstance(element, model.Alternatives):
            part = self.__create_part_from_alternative(element)

        return part

    def __create_part_from_token(self, token):
        arc = fst_model.FSTArc(None, None, token.value, 1.0)

        part = FSTPart()
        part.input_arcs.append(arc)
        part.output_arcs.append(arc)

        return part

    def __create_part_from_rule_reference(self, rule_reference):
        rule = self.grammar.get_rule_with_name(rule_reference.rule_name)

        if rule is not None:
            return self.__create_part_from_rule(rule)

        return None

    def __create_part_from_group(self, group):
        return self.__create_part_from_element(group.value)

    def __create_part_from_optional_group(self, optional_group):
        part = self.__create_part_from_element(optional_group.value)
        part.is_optional = True

        return part

    def __create_part_from_sequence(self, sequence):
        subparts = []

        for element in sequence.elements:
            subpart = self.__create_part_from_element(element)
            subparts.append(subpart)

        part = FSTPart()

        first_subpart = subparts[0]
        last_subpart = subparts[len(subparts) - 1]

        part.input_arcs.extend(first_subpart.input_arcs)
        part.output_arcs.extend(last_subpart.output_arcs)

        optional_output_arcs = []

        for i in range(len(subparts) - 1):
            left_part = subparts[i]
            right_part = subparts[i + 1]

            state = fst_model.FSTState(i)

            for input_arc in left_part.output_arcs:
                input_arc.dest_state = state
                state.inputs.append(input_arc)

            for input_arc in optional_output_arcs:
                new_arc = fst_model.FSTArc(input_arc.src_state, state, input_arc.label, 1.0)
                state.inputs.append(new_arc)

                if input_arc.src_state is not None:
                    input_arc.src_state.outputs.append(new_arc)
                else:
                    part.input_arcs.append(new_arc)

            for input_arc in right_part.input_arcs:
                input_arc.src_state = state
                state.outputs.append(input_arc)

            if right_part.is_optional:
                optional_output_arcs.extend(left_part.output_arcs)
            else:
                optional_output_arcs = []

        for input_arc in optional_output_arcs:
            new_arc = fst_model.FSTArc(input_arc.src_state, None, input_arc.label, input_arc.weight)

            if input_arc.src_state is not None:
                input_arc.src_state.outputs.append(new_arc)
            else:
                part.input_arcs.append(new_arc)

            part.output_arcs.append(new_arc)

        optional_input_arcs = []

        for i in range(len(subparts) - 2, -1, -1):
            left_part = subparts[i]
            right_part = subparts[i + 1]

            if left_part.is_optional:
                optional_input_arcs.extend(right_part.input_arcs)
            else:
                optional_input_arcs = []

        for output_arc in optional_input_arcs:
            new_arc = fst_model.FSTArc(None, output_arc.dest_state, output_arc.label, output_arc.weight)

            if output_arc.dest_state is not None:
                output_arc.dest_state.inputs.append(new_arc)
            else:
                part.output_arcs.append(new_arc)

            part.input_arcs.append(new_arc)

        return part

    def __create_part_from_alternative(self, alternative):
        part = FSTPart()

        for element in alternative.elements:
            subpart = self.__create_part_from_element(element)

            part.input_arcs.extend(subpart.input_arcs)
            part.output_arcs.extend(subpart.output_arcs)

        return part
