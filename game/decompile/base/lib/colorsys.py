# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\colorsys.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 4228 bytes
__all__ = [
 "'rgb_to_yiq'", "'yiq_to_rgb'", "'rgb_to_hls'", "'hls_to_rgb'", 
 "'rgb_to_hsv'", 
 "'hsv_to_rgb'"]
ONE_THIRD = 0.3333333333333333
ONE_SIXTH = 0.16666666666666666
TWO_THIRD = 0.6666666666666666

def rgb_to_yiq(r, g, b):
    y = 0.3 * r + 0.59 * g + 0.11 * b
    i = 0.74 * (r - y) - 0.27 * (b - y)
    q = 0.48 * (r - y) + 0.41 * (b - y)
    return (y, i, q)


def yiq_to_rgb(y, i, q):
    r = y + 0.9468822170900693 * i + 0.6235565819861433 * q
    g = y - 0.27478764629897834 * i - 0.6356910791873801 * q
    b = y - 1.1085450346420322 * i + 1.7090069284064666 * q
    if r < 0.0:
        r = 0.0
    if g < 0.0:
        g = 0.0
    if b < 0.0:
        b = 0.0
    if r > 1.0:
        r = 1.0
    if g > 1.0:
        g = 1.0
    if b > 1.0:
        b = 1.0
    return (
     r, g, b)


def rgb_to_hls(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    l = (minc + maxc) / 2.0
    if minc == maxc:
        return (
         0.0, l, 0.0)
    else:
        if l <= 0.5:
            s = (maxc - minc) / (maxc + minc)
        else:
            s = (maxc - minc) / (2.0 - maxc - minc)
        rc = (maxc - r) / (maxc - minc)
        gc = (maxc - g) / (maxc - minc)
        bc = (maxc - b) / (maxc - minc)
        if r == maxc:
            h = bc - gc
        else:
            if g == maxc:
                h = 2.0 + rc - bc
            else:
                h = 4.0 + gc - rc
    h = h / 6.0 % 1.0
    return (h, l, s)


def hls_to_rgb(h, l, s):
    if s == 0.0:
        return (
         l, l, l)
    elif l <= 0.5:
        m2 = l * (1.0 + s)
    else:
        m2 = l + s - l * s
    m1 = 2.0 * l - m2
    return (_v(m1, m2, h + ONE_THIRD), _v(m1, m2, h), _v(m1, m2, h - ONE_THIRD))


def _v(m1, m2, hue):
    hue = hue % 1.0
    if hue < ONE_SIXTH:
        return m1 + (m2 - m1) * hue * 6.0
    if hue < 0.5:
        return m2
    if hue < TWO_THIRD:
        return m1 + (m2 - m1) * (TWO_THIRD - hue) * 6.0
    return m1


def rgb_to_hsv(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc
    if minc == maxc:
        return (
         0.0, 0.0, v)
    else:
        s = (maxc - minc) / maxc
        rc = (maxc - r) / (maxc - minc)
        gc = (maxc - g) / (maxc - minc)
        bc = (maxc - b) / (maxc - minc)
        if r == maxc:
            h = bc - gc
        else:
            if g == maxc:
                h = 2.0 + rc - bc
            else:
                h = 4.0 + gc - rc
    h = h / 6.0 % 1.0
    return (h, s, v)


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (
         v, v, v)
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return (
         v, t, p)
    if i == 1:
        return (
         q, v, p)
    if i == 2:
        return (
         p, v, t)
    if i == 3:
        return (
         p, q, v)
    if i == 4:
        return (
         t, p, v)
    if i == 5:
        return (
         v, p, q)