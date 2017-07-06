from . import base

from .base import ExtractionStage
from .base import ProcessingStage

from .extraction import SpectrumExtractionStage
from .extraction import MelFilterbankExtractionStage
from .extraction import MFCCExtractionStage

from .scaling import ExponentialStage
from .scaling import LogStage
from .scaling import RescalingStage

from .splicing import SpliceStage
from .splicing import UnspliceMergeType
from .splicing import UnspliceStage

from .convertion import MelToMFCCStage


def mel_extraction_pipeline(win_length=400, win_step=160, num_mel=23):
    return base.Pipeline(extract_stage=MelFilterbankExtractionStage(num_mel=num_mel, win_length=win_length, win_step=win_step))


def mfcc_extraction_pipeline(win_length=400, win_step=160, num_mfcc=13, num_mel=23):
    return base.Pipeline(extract_stage=MFCCExtractionStage(num_mfcc=num_mfcc, num_mel=num_mel, win_length=win_length, win_step=win_step))
