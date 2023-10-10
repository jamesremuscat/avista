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
    INPUT_21 = 21
    INPUT_22 = 22
    INPUT_23 = 23
    INPUT_24 = 24
    INPUT_25 = 25
    INPUT_26 = 26
    INPUT_27 = 27
    INPUT_28 = 28
    INPUT_29 = 29
    INPUT_30 = 30
    INPUT_31 = 31
    INPUT_32 = 32
    INPUT_33 = 33
    INPUT_34 = 34
    INPUT_35 = 35
    INPUT_36 = 36
    INPUT_37 = 37
    INPUT_38 = 38
    INPUT_39 = 39
    INPUT_40 = 40
    COLOUR_BARS = 1000
    COLOUR_1 = 2001
    COLOUR_2 = 2002
    MEDIA_PLAYER_1 = 3010
    MEDIA_PLAYER_1_KEY = 3011
    MEDIA_PLAYER_2 = 3020
    MEDIA_PLAYER_2_KEY = 3021
    MEDIA_PLAYER_3 = 3030
    MEDIA_PLAYER_3_KEY = 3031
    MEDIA_PLAYER_4 = 3040
    MEDIA_PLAYER_4_KEY = 3041
    ME_1_KEY_1_MASK = 4010
    ME_1_KEY_2_MASK = 4020
    ME_1_KEY_3_MASK = 4030
    ME_1_KEY_4_MASK = 4040
    ME_2_KEY_1_MASK = 4050
    ME_2_KEY_2_MASK = 4060
    ME_2_KEY_3_MASK = 4070
    ME_2_KEY_4_MASK = 4080
    ME_3_KEY_1_MASK = 4090
    ME_3_KEY_2_MASK = 4100
    ME_3_KEY_3_MASK = 4110
    ME_3_KEY_4_MASK = 4120
    ME_4_KEY_1_MASK = 4130
    ME_4_KEY_2_MASK = 4140
    ME_4_KEY_3_MASK = 4150
    ME_4_KEY_4_MASK = 4160
    DSK_1_MASK = 5010
    DSK_2_MASK = 5020
    DSK_3_MASK = 5030
    DSK_4_MASK = 5040
    SUPER_SOURCE_1 = 6000
    SUPER_SOURCE_2 = 6001
    CLEAN_FEED_1 = 7001
    CLEAN_FEED_2 = 7002
    CLEAN_FEED_3 = 7003
    CLEAN_FEED_4 = 7004
    AUX_1 = 8001
    AUX_2 = 8002
    AUX_3 = 8003
    AUX_4 = 8004
    AUX_5 = 8005
    AUX_6 = 8006
    AUX_7 = 8007
    AUX_8 = 8008
    AUX_9 = 8009
    AUX_10 = 8010
    AUX_11 = 8011
    AUX_12 = 8012
    AUX_13 = 8013
    AUX_14 = 8014
    AUX_15 = 8015
    AUX_16 = 8016
    AUX_17 = 8017
    AUX_18 = 8018
    AUX_19 = 8019
    AUX_20 = 8020
    AUX_21 = 8021
    AUX_22 = 8022
    AUX_23 = 8023
    AUX_24 = 8024
    ME_1_PROGRAM = 10010
    ME_1_PREVIEW = 10011
    ME_2_PROGRAM = 10020
    ME_2_PREVIEW = 10021
    ME_3_PROGRAM = 10030
    ME_3_PREVIEW = 10031
    ME_4_PROGRAM = 10040
    ME_4_PREVIEW = 10041


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
    VIDEO_MODE_26 = 26
    VIDEO_MODE_27 = 27
    VIDEO_MODE_28 = 28
    VIDEO_MODE_29 = 29


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
    INPUT_21 = 21
    INPUT_22 = 22
    INPUT_23 = 23
    INPUT_24 = 24
    INPUT_25 = 25
    INPUT_26 = 26
    INPUT_27 = 27
    INPUT_28 = 28
    INPUT_29 = 29
    INPUT_30 = 30
    INPUT_31 = 31
    INPUT_32 = 32
    INPUT_33 = 33
    INPUT_34 = 34
    INPUT_35 = 35
    INPUT_36 = 36
    INPUT_37 = 37
    INPUT_38 = 38
    INPUT_39 = 39
    INPUT_40 = 40
    XLR = 1001
    AES_EBU = 1101
    RCA = 1201
    MEDIA_PLAYER_1 = 2001
    MEDIA_PLAYER_2 = 2002
    MEDIA_PLAYER_3 = 2003
    MEDIA_PLAYER_4 = 2004


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
    LAYOUT_15 = 15


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


class MacroActionType(IntEnum):
    RUN_MACRO = 0
    STOP = 1
    STOP_RECORDING = 2
    INSERT_WAIT = 3
    CONTINUE = 4
    DELETE = 5
