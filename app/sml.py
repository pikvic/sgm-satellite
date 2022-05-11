import math as m
import numpy as np

class ProjMapper:
    '''Class for georeferencing Lab34 projs'''
    def __init__(self, pt, lon, lat, lon_size, lat_size, lon_res, lat_res):
        self.pt = pt
        lon = m.radians(lon)
        lat = m.radians(lat)
        lon_size = m.radians(lon_size)
        lat_size = m.radians(lat_size)
        lon_res = m.radians(lon_res)
        lat_res = m.radians(lat_res)

        if self.pt == 0:
            m1 = m.log(m.tan(0.5 * lat + 0.25 * m.pi))
            m2 = m.log(m.tan(0.5 * (lat + lat_size) + 0.25 * m.pi))
            self.size_y = int((m2 - m1) / lat_res + 0.5) + 1
            self.lat_a = (self.size_y - 1) / (m2 - m1)
            self.lat_b = -self.lat_a * m1
            self.size_x = int(lon_size / lon_res + 0.5) + 1
            self.lon_a = (self.size_x - 1) / lon_size
            self.lon_b = -self.lon_a * lon
        if self.pt == 1:
            self.size_y = int(lat_size / lat_res + 0.5) + 1
            self.lat_a = (self.size_y - 1) / lat_size
            self.lat_b = -self.lat_a * lat
            self.size_x = int(lon_size / lon_res + 0.5) + 1
            self.lon_a = int(self.size_x - 1) / lon_size
            self.lon_b = -self.lon_a * lon

    def lat(self, scan):
        scan = self.size_y - scan - 1
        if self.pt == 0:
            return m.degrees(2.0 * m.atan(m.exp((scan - self.lat_b) / self.lat_a)) - m.pi / 2.0)
        if self.pt == 1:
            return m.degrees((scan - self.lat_b) / self.lat_a)

    def lon(self, column):
        return m.degrees((column - self.lon_b) / self.lon_a)

    def scan(self, lat):
        lat = m.radians(lat)
        if self.pt == 0:
            return self.size_y - int(m.log(m.tan(0.5 * lat + 0.25 * m.pi)) * self.lat_a + self.lat_b + 1e-12) - 1
        if self.pt == 1:
            return self.size_y - int(lat * self.lat_a + self.lat_b + 1e-12) - 1

    def column(self, lon):
        lon = m.radians(lon)
        return int(lon * self.lon_a + self.lon_b + 1e-12)
    
# Blocks

# Common
b0_common_dt = np.dtype([
    ("formatType", np.uint8),
    ("satName", "S13"),
    ("satId", np.uint32),
    ("revNum", np.uint32),
    ("year", np.uint16),
    ("day", np.uint16),
    ("dayTime", np.uint32),
    ("o_year", np.uint16),
    ("o_day", np.uint16),
    ("o_time", np.uint32),
    ("reserved", (np.uint8, 23)),
    ("receiver", np.uint8),
    ("dataType1", np.uint8),
    ("dataType2", np.uint8),
])

# Proj Common
b0_proj_common_dt = np.dtype([
    ("processLevel", np.uint32),
    ("channel", np.uint16),
    ("maxPixelValue", np.uint16),
    ("projType", np.uint16),
    ("scanNum", np.uint16),
    ("pixNum", np.uint16),
    ("lat", np.float32),
    ("lon", np.float32),
    ("latSize", np.float32),
    ("lonSize", np.float32),
    ("latRes", np.float32),
    ("lonRes", np.float32),
])

# NORAD
b0_norad_dt = np.dtype([
    ("NORADrevNum", np.uint32),
    ("setNum", np.uint16),
    ("ephemType", np.uint16),
    ("NORADyear", np.uint16),
    ("yearTime", np.float64),
    ("n0", np.float64),
    ("bstar", np.float64),
    ("i0", np.float64),
    ("raan", np.float64),
    ("e0", np.float64),
    ("w0", np.float64),
    ("m0", np.float64),
    ("dataName", "S32"),
    ("dataUnitsName", "S22"),
])

# Corparams
b0_corparams_dt = np.dtype([
    ("corVersion", np.uint16),
    ("orbitModelType", np.uint16),
    ("corTime", np.int16),
    ("corRoll", np.float64),
    ("corPitch", np.float64),
    ("corYaw", np.float64),
    ("gravitModel", np.uint16),
    ("spare", (np.uint8, 512 - 288)),
])

# Types

# Projection
b0_proj_dt = np.dtype([
    # common
    ("b0_common", b0_common_dt),
    # proj_common
    ("b0_proj_common", b0_proj_common_dt),
    # proj_specific
    ("ka", np.float64),
    ("kb", np.float64),
    ("channelName", "S10"),
    # NORAD
    ("b0_norad", b0_norad_dt),
    # CorParams
    ("b0_corparams", b0_corparams_dt),
])

# DOTC
b0_dotc_dt = np.dtype([
    # common
    ("b0_common", b0_common_dt),
    # proj_common
    ("b0_proj_common", b0_proj_common_dt),
    # dotc_specific
    ("algo", np.uint16),
    ("nsect", np.uint16),
    ("win_grad", np.uint16),
    ("win_ever", np.uint16),
    ("step_x", np.uint16),
    ("step_y", np.uint16),
    ("step_grad", np.uint16),
    ("step_ever", np.uint16),
    ("signif", np.uint16),
    ("reserved1", (np.uint8, 8)),
    # NORAD
    ("b0_norad", b0_norad_dt),
    # CorParams
    ("b0_corparams", b0_corparams_dt),
])


def readproj(fname):
    f = open(fname, 'rb')
    b0 = np.fromfile(f, dtype=b0_proj_dt, count=1)
    sizeX = b0['b0_proj_common']['pixNum'][0]
    sizeY = b0['b0_proj_common']['scanNum'][0]
    data = np.fromfile(f, dtype='int16')
    data = data.reshape(sizeY, sizeX)
    data = np.flipud(data)
    f.close()
    return b0, data

def readproj2(buffer):
    b0 = np.frombuffer(buffer[:512], dtype=b0_proj_dt, count=1)
    sizeX = b0['b0_proj_common']['pixNum'][0]
    sizeY = b0['b0_proj_common']['scanNum'][0]
    data = np.frombuffer(buffer[512:], dtype='int16')
    data = data.reshape(sizeY, sizeX)
    data = np.flipud(data)
    return b0, data

def get_projmapper(b0):
    lon = b0['b0_proj_common']['lon'][0]
    lat = b0['b0_proj_common']['lat'][0]
    latsize = b0['b0_proj_common']['latSize'][0]
    lonsize = b0['b0_proj_common']['lonSize'][0]
    latres = b0['b0_proj_common']['latRes'][0]
    lonres = b0['b0_proj_common']['lonRes'][0]
    rows = b0['b0_proj_common']['scanNum'][0]
    cols = b0['b0_proj_common']['pixNum'][0]
    pt = b0['b0_proj_common']['projType'][0] - 1
    return ProjMapper(pt, lon, lat, lonsize, latsize, lonres, latres)