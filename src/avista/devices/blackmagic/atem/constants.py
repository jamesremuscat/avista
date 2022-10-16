from enum import IntEnum


class VideoSource(IntEnum):
    BLACK = 0
    INPUT_1 = 1
    INPUT_2 = 2
    INPUT_3 = 3
    INPUT_4 = 4
    INPUT_5 = 5
    INPUT_6 = 6
    INPUT_7 = 7
    INPUT_8 = 8
    INPUT_9 = 9
    INPUT_10 = 10
    INPUT_11 = 11
    INPUT_12 = 12
    INPUT_13 = 13
    INPUT_14 = 14
    INPUT_15 = 15
    INPUT_16 = 16
    INPUT_17 = 17
    INPUT_18 = 18
    INPUT_19 = 19
    INPUT_20 = 20
    COLOUR_BARS = 1000
    COLOUR_1 = 2001
    COLOUR_2 = 2002
    MEDIA_PLAYER_1 = 3010
    MEDIA_PLAYER_1_KEY = 3011
    MEDIA_PLAYER_2 = 3020
    MEDIA_PLAYER_2_KEY = 3021
    KEY_1_MASK = 4010
    KEY_2_MASK = 4020
    KEY_3_MASK = 4030
    KEY_4_MASK = 4040
    DSK_1_MASK = 5010
    DSK_2_MASK = 5020
    SUPER_SOURCE = 6000
    CLEAN_FEED_1 = 7001
    CLEAN_FEED_2 = 7002
    AUX_1 = 8001
    AUX_2 = 8002
    AUX_3 = 8003
    AUX_4 = 8004
    AUX_5 = 8005
    AUX_6 = 8006
    ME_1_PROGRAM = 10010
    ME_1_PREVIEW = 10011
    ME_2_PROGRAM = 10020
    ME_2_PREVIEW = 10021


class ExternalPortType(IntEnum):
    NONE = 0
    SDI = 1
    HDMI = 2
    COMPOSITE = 3
    COMPONENT = 4
    SVIDEO = 16
    INTERNAL = 256


class InternalPortType(IntEnum):
    EXTERNAL = 0
    BLACK = 1
    COLOR_BARS = 2
    COLOR_GENERATOR = 3
    MEDIA_PLAYER_FILL = 4
    MEDIA_PLAYER_KEY = 5
    SUPER_SOURCE = 6
    EXTERNAL_DIRECT = 7
    ME_OUTPUT = 128
    AUXILIARY = 129
    MASK = 130
    MULTIVIEWER = 131


class SourceAvailability(IntEnum):
    NONE = 0
    AUXES = 1 << 0,
    MULTIVIEWER = 1 << 1,
    SUPER_SOURCE_ART = 1 << 2,
    SUPER_SOURCE_BOX = 1 << 3,
    KEY_SOURCE = 1 << 4


class MEAvailability(IntEnum):
    NONE = 0
    ME_1 = 1
    ME_2 = 2
    ME_3 = 4
    ME_4 = 8


class MediaPoolFileType(IntEnum):
    STILL = 0
    CLIP_1 = 1
    CLIP_2 = 2
    CLIP_3 = 3
    CLIP_4 = 4


class VideoMode(IntEnum):
    NONE = -1
    NTSC_525I = 0
    PAL_625I = 1
    NTSC_525I_16_9 = 2
    PAL_625I_16_9 = 3
    HD_720_50 = 4
    HD_720_59 = 5
    HD_1080I_50 = 6
    HD_1080I_59 = 7
    HD_1080P_23 = 8
    HD_1080P_24 = 9
    HD_1080P_25 = 10
    HD_1080P_29 = 11
    HD_1080P_50 = 12
    HD_1080P_59 = 13
    HD_4K_23 = 14
    HD_4K_24 = 15
    HD_4K_25 = 16
    HD_4K_29 = 17


class AudioSource(IntEnum):
    INPUT_1 = 1
    INPUT_2 = 2
    INPUT_3 = 3
    INPUT_4 = 4
    INPUT_5 = 5
    INPUT_6 = 6
    INPUT_7 = 7
    INPUT_8 = 8
    INPUT_9 = 9
    INPUT_10 = 10
    INPUT_11 = 11
    INPUT_12 = 12
    INPUT_13 = 13
    INPUT_14 = 14
    INPUT_15 = 15
    INPUT_16 = 16
    INPUT_17 = 17
    INPUT_18 = 18
    INPUT_19 = 19
    INPUT_20 = 20
    XLR = 1001
    AES_EBU = 1101
    RCA = 1201
    MEDIA_PLAYER_1 = 2001
    MEDIA_PLAYER_2 = 2002


class AudioSourceType(IntEnum):
    EXTERNAL_VIDEO = 0
    MEDIA_PLAYER = 1
    EXTERNAL_AUDIO = 2


class AudioSourcePlugType(IntEnum):
    INTERNAL = 0
    SDI = 1
    HDMI = 2
    COMPONENT = 3
    COMPOSITE = 4
    SVIDEO = 5
    XLR = 32
    AES_EBU = 64
    RCA = 128


class AudioMixOption(IntEnum):
    OFF = 0
    ON = 1
    AFV = 2


class MultiviewLayout(IntEnum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class MultiviewLayoutV8(IntEnum):
    DEFAULT = 0,
    TOP_LEFT_SMALL = 1,
    TOP_RIGHT_SMALL = 2,
    PROGRAM_BOTTOM = 3,
    BOTTOM_LEFT_SMALL = 4,
    PROGRAM_RIGHT = 5,
    BOTTOM_RIGHT_SMALL = 8,
    PROGRAM_LEFT = 10,
    PROGRAM_TOP = 12


class TransitionStyle(IntEnum):
    MIX = 0
    DIP = 1
    WIPE = 2
    DVE = 3
    STING = 4


class KeyType(IntEnum):
    LUMA = 0
    CHROMA = 1
    PATTERN = 2
    DVE = 3


class SDI3GOutputLevel(IntEnum):
    LEVEL_B = 0
    LEVEL_A = 1


class BevelType(IntEnum):
    NONE = 0
    IN_OUT = 1
    IN = 2
    OUT = 3


class PatternStyle(IntEnum):
    LINEAR_X = 0
    LINEAR_Y = 1
    BILINEAR_X = 2
    BILINEAR_Y = 3
    CROSS = 4
    SQUARE_CENTRE = 5
    DIAMOND = 6
    CIRCLE = 7
    SQUARE_TOP_LEFT = 8
    SQUARE_BOTTOM_LEFT = 9
    SQUARE_BOTTOM_RIGHT = 10
    SQUARE_TOP_RIGHT = 11
    SQUARE_TOP = 12
    SQUARE_BOTTOM = 13
    SQUARE_LEFT = 14
    SQUARE_RIGHT = 15
    DIAGONAL_TOP_LEFT = 16
    DIAGONAL_TOP_RIGHT = 17
