import os
from ctypes import *
import struct
import platform
from enum import Enum
from functools import wraps


def pause():
    input("Press Enter to continue ...")


def get_lib_path():
    lib_base = "../../SDK"
    if platform.system() == 'Windows':
        if struct.calcsize("P") == 4:
            lib_name = "windows/MECG20x86.dll"
        else:
            lib_name = "windows/MECG20x64.dll"
    elif platform.system() == 'Linux':
        if platform.machine() == 'aarch64':
            lib_name = "linux/libmecgrpix64.so"
        elif platform.machine() == 'armv7l':
            lib_name = "linux/libmecgrpix86.so"
        elif platform.machine() == 'x86_64':
            lib_name = "linux/libmecgx64.so"
        else:
            lib_name = "linux/libmecgx86.so"
    elif platform.system() == 'Darwin':
        lib_name = "macos/libmecg.a"

    return os.path.join(lib_base, lib_name)

class VoltageArray(Structure):
    _fields_ = [("voltage", c_double * 12)]

class CTSCSE_Database (Enum):
    CTSCSE_ANE20000 = 0
    CTSCSE_ANE20001 = 1
    CTSCSE_ANE20002 = 2
    CTSCSE_CAL05000 = 3
    CTSCSE_CAL10000 = 4
    CTSCSE_CAL15000 = 5
    CTSCSE_CAL20000 = 6
    CTSCSE_CAL20002 = 7
    CTSCSE_CAL20100 = 8
    CTSCSE_CAL20110 = 9
    CTSCSE_CAL20160 = 10
    CTSCSE_CAL20200 = 11
    CTSCSE_CAL20210 = 12
    CTSCSE_CAL20260 = 13
    CTSCSE_CAL20500 = 14
    CTSCSE_CAL20502 = 15
    CTSCSE_CAL30000 = 16
    CTSCSE_CAL40000 = 17
    CTSCSE_CAL50000 = 18
    CTSCSE_PCTH001 = 19   # MA1 series
    CTSCSE_PCTH002 = 20
    CTSCSE_PCTH003 = 21
    CTSCSE_PCTH004 = 22
    CTSCSE_PCTH005 = 23
    CTSCSE_PCTH007 = 24
    CTSCSE_PCTH008 = 25
    CTSCSE_PCTH009 = 26
    CTSCSE_PCTH011 = 27
    CTSCSE_PCTH012 = 28
    CTSCSE_PCTH013 = 29
    CTSCSE_PCTH014 = 30
    CTSCSE_PCTH015 = 31
    CTSCSE_PCTH016 = 32
    CTSCSE_PCTH017 = 33
    CTSCSE_PCTH019 = 34
    CTSCSE_PCTH021 = 35
    CTSCSE_PCTH022 = 36
    CTSCSE_PCTH024 = 37
    CTSCSE_PCTH025 = 38
    CTSCSE_PCTH026 = 39
    CTSCSE_PCTH027 = 40
    CTSCSE_PCTH028 = 41
    CTSCSE_PCTH029 = 42
    CTSCSE_PCTH030 = 43
    CTSCSE_PCTH031 = 44
    CTSCSE_PCTH032 = 45
    CTSCSE_PCTH033 = 46
    CTSCSE_PCTH034 = 47
    CTSCSE_PCTH035 = 48
    CTSCSE_PCTH036 = 49
    CTSCSE_PCTH037 = 50
    CTSCSE_PCTH038 = 51
    CTSCSE_PCTH039 = 52
    CTSCSE_PCTH040 = 53
    CTSCSE_PCTH041 = 54
    CTSCSE_PCTH042 = 55
    CTSCSE_PCTH043 = 56
    CTSCSE_PCTH044 = 57
    CTSCSE_PCTH046 = 58
    CTSCSE_PCTH047 = 59
    CTSCSE_PCTH048 = 60
    CTSCSE_PCTH049 = 61
    CTSCSE_PCTH051 = 62
    CTSCSE_PCTH053 = 63
    CTSCSE_PCTH055 = 64
    CTSCSE_PCTH058 = 65
    CTSCSE_PCTH059 = 66
    CTSCSE_PCTH060 = 67
    CTSCSE_PCTH061 = 68
    CTSCSE_PCTH062 = 69
    CTSCSE_PCTH063 = 70
    CTSCSE_PCTH064 = 71
    CTSCSE_PCTH065 = 72
    CTSCSE_PCTH066 = 73
    CTSCSE_PCTH068 = 74
    CTSCSE_PCTH069 = 75
    CTSCSE_PCTH071 = 76
    CTSCSE_PCTH072 = 77
    CTSCSE_PCTH073 = 78
    CTSCSE_PCTH074 = 79
    CTSCSE_PCTH075 = 80
    CTSCSE_PCTH076 = 81
    CTSCSE_PCTH077 = 82
    CTSCSE_PCTH078 = 83
    CTSCSE_PCTH079 = 84
    CTSCSE_PCTH080 = 85
    CTSCSE_PCTH081 = 86
    CTSCSE_PCTH082 = 87
    CTSCSE_PCTH083 = 88
    CTSCSE_PCTH084 = 89
    CTSCSE_PCTH085 = 90
    CTSCSE_PCTH086 = 91
    CTSCSE_PCTH087 = 92
    CTSCSE_PCTH088 = 93
    CTSCSE_PCTH090 = 94
    CTSCSE_PCTH091 = 95
    CTSCSE_PCTH095 = 96
    CTSCSE_PCTH096 = 97
    CTSCSE_PCTH097 = 98
    CTSCSE_PCTH098 = 99
    CTSCSE_PCTH099 = 100
    CTSCSE_PCTH101 = 101
    CTSCSE_PCTH102 = 102
    CTSCSE_PCTH103 = 103
    CTSCSE_PCTH104 = 104
    CTSCSE_PCTH105 = 105
    CTSCSE_PCTH106 = 106
    CTSCSE_PCTH107 = 107
    CTSCSE_PCTH108 = 108
    CTSCSE_PCTH110 = 109
    CTSCSE_PCTH112 = 110
    CTSCSE_PCTH113 = 111
    CTSCSE_PCTH114 = 112
    CTSCSE_PCTH115 = 113
    CTSCSE_PCTH116 = 114
    CTSCSE_PCTH118 = 115
    CTSCSE_PCTH123 = 116
    CTSCSE_PCTH124 = 117
    CTSCSE_PCTH125 = 118
    CTSCSE_MAX = 119


class CTSCSE_Noise (Enum):
    CTSCSENoise_50HZ = 0         # 50Hz noise 25uV peak
    CTSCSENoise_60HZ = 1         # 60Hz noise 25uV peak
    CTSCSENoise_BL = 2           # Baseline noise 0.3Hz 0.5mV peak
    CTSCSENoise_BL_HF = 3        # Baseline noise 0.3Hz 0.5mV peak + HF noise 15uVrms
    CTSCSENoise_HF_05 = 4        # HF noise 05uVrms
    CTSCSENoise_HF_10 = 5        # HF noise 10uVrms
    CTSCSENoise_HF_15 = 6        # HF noise 15uVrms
    CTSCSENoise_HF_20 = 7        # HF noise 20uVrms
    CTSCSENoise_HF_25 = 8        # HF noise 25uVrms
    CTSCSENoise_HF_30 = 9        # HF noise 30uVrms
    CTSCSENoise_HF_35 = 10       # HF noise 35uVrms
    CTSCSENoise_HF_40 = 11       # HF noise 40uVrms
    CTSCSENoise_HF_45 = 12       # HF noise 45uVrms
    CTSCSENoise_HF_50 = 13       # HF noise 50uVr
    CTSCSENoise_MAX = 14         # Noise Off


class ECG_Lead (Enum):
    ECG_Lead_I = 0
    ECG_Lead_II = 1
    ECG_Lead_V1 = 2
    ECG_Lead_V2 = 3
    ECG_Lead_V3 = 4
    ECG_Lead_V4 = 5
    ECG_Lead_V5 = 6
    ECG_Lead_V6 = 7
    ECG_Lead_None = 8


class WAVEFORM_TYPE (Enum):
    WaveformSine = 0
    WaveformTriangle = 1
    WaveformSquare = 2


class MODEL_INFORMATION (Structure):
    _fields_ = [
        ('ProductName', c_char * 16),
        ('SerialNumber', c_char * 16)
    ]


class ECG_SIGNAL (Structure):
    _fields_ = [
        ('Description', c_char * 16),
        ('MappingLead', c_int)
    ]


class ECG_HEADER (Structure):
    _fields_ = [
        ('RecordName', c_char * 16),
        ('NumberOfSignals', c_long),
        ('SamplingFrequency', c_long),
        ('NumberOfSamplesPerSignal', c_long),
        ('Reserved', c_ubyte * 16),
        ('Signal', ECG_SIGNAL)
    ]

def sdk_fn(cfn_name, args_type=None, return_type=None):
    def decorator_function(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cfn = getattr(self.sdk, cfn_name)
            if args_type:
                cfn.argtypes = args_type
            if return_type:
                cfn.restype = return_type
            return cfn(*args, **kwargs)

        return wrapper

    return decorator_function

ConnectedCallback = CFUNCTYPE(None, c_bool)
OutputSignalCallback = CFUNCTYPE(None, c_double, c_double * 12, c_bool)
OutputSignalExCallback = CFUNCTYPE(None, c_double, c_double, POINTER(VoltageArray), c_bool)
OutputDelayCallback = CFUNCTYPE(None, c_int)

class MECG20:
    def __init__(self, lib_file_path):        
        self.sdk = cdll.LoadLibrary(lib_file_path) 

    #
    # Initialization & Cleanup
    #
    @sdk_fn("MECGInit", [ConnectedCallback], c_bool)
    def init(self, cb) -> c_bool:
        pass

    @sdk_fn("MECGConnect", [c_uint, c_uint], c_bool)
    def connect(self, port_number, milliseconds_timeout) -> c_bool:
        pass

    @sdk_fn("MECGFree", [], None)
    def free(self) -> None:
        pass

    @sdk_fn("MECGGetVersion", [], c_uint32)
    def get_version(self) -> c_uint32:
        pass

    #
    # Device Configurations
    #
    def get_serial_number(self):
        self.sdk.MECGGetSerialNumber.restype = c_char_p
        return self.sdk.MECGGetSerialNumber().decode('ascii')

    #
    # Load *.hea/*.dat database
    #
    @sdk_fn("MECGLoadMITHeader", [c_char_p], POINTER(ECG_HEADER))
    def load_mit_header(self, file_path) -> POINTER(ECG_HEADER):
        pass

    @sdk_fn("MECGLoadMITDatabase", [c_void_p], c_bool)
    def load_mit_database(self, ecg_header) -> c_bool:
        pass

    @sdk_fn("MECGFreeECGHeader", [c_void_p], None)
    def free_ecg_header(self, ecg_header) -> None:
        pass

    #
    # Load AHA database
    #
    @sdk_fn("MECGLoadDatabaseAHA", [c_char_p], POINTER(ECG_HEADER))
    def load_aha_database(self, file_path) -> POINTER(ECG_HEADER):
        pass

    #
    # Load CSE database
    #
    @sdk_fn("MECGLoadDatabaseCSE", [c_char_p], POINTER(ECG_HEADER))
    def load_cse_database(self, file_path) -> POINTER(ECG_HEADER):
        pass

    #
    # Load CTS/CSE database
    #
    @sdk_fn("MECGLoadDatabaseCTS_CSE", [c_int, c_int], POINTER(ECG_HEADER))
    def load_cts_cse_database(self, database, noise) -> POINTER(ECG_HEADER):
        pass

    #
    # Load WhaleTeq-format database
    #
    @sdk_fn("MECGLoadDatabaseWhaleTeq", [c_char_p], POINTER(ECG_HEADER))
    def load_whaleteq_database(self, file_path) -> POINTER(ECG_HEADER):
        pass

    #
    # Load periodic waveform
    #
    @sdk_fn("MECGLoadWaveform", [c_int, c_double, c_double], c_bool)
    def load_waveform(self, waveform_type, frequency, amplitude) -> c_bool:
        pass

    @sdk_fn("MECGLoadWaveformRectanglePulse", [c_int, c_double, c_double], c_bool)
    def load_waveform_rectangle_pulse(self, pulse_width, frequency, amplitude) -> c_bool:
        pass

    @sdk_fn("MECGLoadWaveformTrianglePulse", [c_int, c_double, c_double], c_bool)
    def load_waveform_triangle_pulse(self, pulse_width, frequency, amplitude) -> c_bool:
        pass

    @sdk_fn("MECGEnableLoop", [c_bool], None)
    def enable_loop(self, enable) -> None:
        pass

    @sdk_fn("MECGOutputWaveform", [c_int, c_void_p, c_void_p], c_bool)
    def output_waveform(self, start_position, cb_output, cb_delay) -> c_bool:
        pass
    
    @sdk_fn("MECGStopOutput", [], None)
    def stop_output(self) -> None:
        pass