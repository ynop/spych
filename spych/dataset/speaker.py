import enum

SPEAKER_INFO_GENDER = 'gender'
SPEAKER_INFO_SYNTHESIZED = 'synthesized'
SPEAKER_INFO_SYNTHESIZER_VOICE = 'synthesizer_voice'
SPEAKER_INFO_SYNTHESIZER_EFFECTS = 'synthesizer_effects'
SPEAKER_INFO_SYNTHESIZER_TOOL = 'synthesizer_tool'


class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2


class Speaker(object):
    def __init__(self, idx, gender=None):
        self.idx = idx

        if gender == 'm':
            gender = Gender.MALE
        elif gender == 'f':
            gender = Gender.FEMALE

        self.gender = gender

        self.is_synthesized = False
        self.synthesis_voice = None
        self.synthesis_effects = None
        self.synthesis_tool = None

    def load_speaker_info_from_dict(self, speaker_info):
        if SPEAKER_INFO_GENDER in speaker_info.keys():
            gender = speaker_info[SPEAKER_INFO_GENDER]

            if gender == 'm':
                self.gender = Gender.MALE
            elif gender == 'f':
                self.gender = Gender.FEMALE

        if SPEAKER_INFO_SYNTHESIZED in speaker_info.keys():
            self.is_synthesized = speaker_info[SPEAKER_INFO_SYNTHESIZED]

        if SPEAKER_INFO_SYNTHESIZER_VOICE in speaker_info.keys():
            self.synthesis_voice = speaker_info[SPEAKER_INFO_SYNTHESIZER_VOICE]

        if SPEAKER_INFO_SYNTHESIZER_EFFECTS in speaker_info.keys():
            self.synthesis_effects = speaker_info[SPEAKER_INFO_SYNTHESIZER_EFFECTS]

        if SPEAKER_INFO_SYNTHESIZER_TOOL in speaker_info.keys():
            self.synthesis_tool = speaker_info[SPEAKER_INFO_SYNTHESIZER_TOOL]

    def get_speaker_info_dict(self):
        speaker_info = {}

        if self.gender == Gender.MALE:
            speaker_info[SPEAKER_INFO_GENDER] = 'm'
        elif self.gender == Gender.FEMALE:
            speaker_info[SPEAKER_INFO_GENDER] = 'f'

        speaker_info[SPEAKER_INFO_SYNTHESIZED] = self.is_synthesized

        if self.synthesis_tool is not None:
            speaker_info[SPEAKER_INFO_SYNTHESIZER_TOOL] = self.synthesis_tool

        if self.synthesis_voice is not None:
            speaker_info[SPEAKER_INFO_SYNTHESIZER_VOICE] = self.synthesis_voice

        if self.synthesis_effects is not None:
            speaker_info[SPEAKER_INFO_SYNTHESIZER_EFFECTS] = self.synthesis_effects

        return speaker_info