#!/usr/bin/env python3
"""
Cat OS 1.X - A Windows NT 1.0 Style Operating System Simulation
By Team Flames / Samsoft
Features: Procedural Vista-style boot chime, NT 1.0 aesthetic, cat-themed UI
"""

import pygame
import pygame.gfxdraw
import math
import random
import struct
import io
import time
from datetime import datetime

# Initialize pygame
pygame.init()
AUDIO_AVAILABLE = False
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except:
    print("Audio not available - running without sound")

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cat OS 1.X - Team Flames")

# NT 1.0 Color Palette
COLORS = {
    'desktop': (0, 128, 128),      # Teal desktop
    'window_bg': (192, 192, 192),  # Light gray
    'window_dark': (128, 128, 128), # Dark gray
    'window_light': (255, 255, 255), # White highlight
    'window_shadow': (64, 64, 64),  # Shadow
    'title_active': (0, 0, 128),    # Navy blue title bar
    'title_inactive': (128, 128, 128),
    'title_text': (255, 255, 255),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'button_face': (192, 192, 192),
    'menu_bar': (192, 192, 192),
    'selection': (0, 0, 128),
    'cat_orange': (255, 165, 0),
    'cat_pink': (255, 182, 193),
}

# ============== PROCEDURAL AUDIO ENGINE ==============

def generate_sine_wave(freq, duration, volume=0.3, sample_rate=44100):
    """Generate a sine wave"""
    samples = int(sample_rate * duration)
    wave = []
    for i in range(samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * freq * t) * volume
        wave.append(value)
    return wave

def generate_envelope(samples, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
    """ADSR envelope"""
    total = len(samples)
    envelope = []
    attack_samples = int(total * attack)
    decay_samples = int(total * decay)
    release_samples = int(total * release)
    sustain_samples = total - attack_samples - decay_samples - release_samples
    
    for i in range(attack_samples):
        envelope.append(i / attack_samples)
    for i in range(decay_samples):
        envelope.append(1.0 - (1.0 - sustain) * (i / decay_samples))
    for i in range(sustain_samples):
        envelope.append(sustain)
    for i in range(release_samples):
        envelope.append(sustain * (1.0 - i / release_samples))
    
    while len(envelope) < total:
        envelope.append(0)
    
    return [samples[i] * envelope[i] for i in range(min(len(samples), len(envelope)))]

def mix_waves(*waves):
    """Mix multiple waves together"""
    max_len = max(len(w) for w in waves)
    result = [0.0] * max_len
    for wave in waves:
        for i, sample in enumerate(wave):
            result[i] += sample
    # Normalize
    max_val = max(abs(s) for s in result) or 1
    return [s / max_val * 0.8 for s in result]

def generate_vista_chime():
    """Generate a Vista-style boot chime - ethereal, layered, hopeful"""
    sample_rate = 44100
    
    # Vista chime characteristics: layered pads, ascending melody, shimmer
    # Key: G major, ethereal feel
    
    # Base pad chord (G major with add9) - sustained
    pad_g = generate_sine_wave(196.00, 3.5, 0.15)  # G3
    pad_b = generate_sine_wave(246.94, 3.5, 0.12)  # B3
    pad_d = generate_sine_wave(293.66, 3.5, 0.12)  # D4
    pad_a = generate_sine_wave(220.00, 3.5, 0.08)  # A3 (add9)
    
    # Apply envelope to pad
    pad_g = generate_envelope(pad_g, 0.3, 0.1, 0.5, 0.3)
    pad_b = generate_envelope(pad_b, 0.35, 0.1, 0.5, 0.3)
    pad_d = generate_envelope(pad_d, 0.4, 0.1, 0.5, 0.3)
    pad_a = generate_envelope(pad_a, 0.45, 0.1, 0.5, 0.3)
    
    # Melody notes (bell-like, ascending)
    def bell_tone(freq, start_time, duration=0.8):
        wave = generate_sine_wave(freq, duration, 0.25)
        # Add harmonics for bell quality
        h2 = generate_sine_wave(freq * 2, duration, 0.1)
        h3 = generate_sine_wave(freq * 3, duration, 0.05)
        combined = mix_waves(wave, h2, h3)
        combined = generate_envelope(combined, 0.01, 0.15, 0.3, 0.54)
        
        # Pad with silence for timing
        silence_before = [0.0] * int(sample_rate * start_time)
        return silence_before + combined
    
    # Ascending melody: G4 -> B4 -> D5 -> G5
    melody1 = bell_tone(392.00, 0.0, 0.9)    # G4
    melody2 = bell_tone(493.88, 0.4, 0.9)    # B4
    melody3 = bell_tone(587.33, 0.8, 0.9)    # D5
    melody4 = bell_tone(783.99, 1.2, 1.2)    # G5 (longer, final)
    
    # Shimmer/sparkle effect
    def shimmer(base_freq, start, duration=0.5):
        wave = []
        samples = int(sample_rate * duration)
        for i in range(samples):
            t = i / sample_rate
            # Slight pitch wobble
            freq = base_freq * (1 + 0.003 * math.sin(t * 30))
            value = math.sin(2 * math.pi * freq * t) * 0.08
            # Tremolo
            value *= (0.7 + 0.3 * math.sin(t * 15))
            wave.append(value)
        wave = generate_envelope(wave, 0.1, 0.2, 0.3, 0.4)
        silence = [0.0] * int(sample_rate * start)
        return silence + wave
    
    shimmer1 = shimmer(1567.98, 1.5, 1.0)  # G6
    shimmer2 = shimmer(1975.53, 1.7, 0.8)  # B6
    
    # Sub bass for warmth
    sub = generate_sine_wave(98.00, 3.0, 0.1)  # G2
    sub = generate_envelope(sub, 0.5, 0.1, 0.3, 0.3)
    
    # Mix everything
    final = mix_waves(pad_g, pad_b, pad_d, pad_a, 
                      melody1, melody2, melody3, melody4,
                      shimmer1, shimmer2, sub)
    
    # Convert to stereo 16-bit
    stereo_data = []
    for sample in final:
        val = int(sample * 32767)
        val = max(-32768, min(32767, val))
        stereo_data.append(struct.pack('<hh', val, val))
    
    return b''.join(stereo_data)

def play_boot_chime():
    """Play the boot chime"""
    if not AUDIO_AVAILABLE:
        return None
    chime_data = generate_vista_chime()
    sound = pygame.mixer.Sound(buffer=chime_data)
    sound.play()
    return sound

# ============== 8x8 BITMAP FONT ==============

FONT_8X8 = {
    ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
    '!': [0x18,0x18,0x18,0x18,0x18,0x00,0x18,0x00],
    '"': [0x6C,0x6C,0x24,0x00,0x00,0x00,0x00,0x00],
    '#': [0x6C,0x6C,0xFE,0x6C,0xFE,0x6C,0x6C,0x00],
    '$': [0x18,0x3E,0x60,0x3C,0x06,0x7C,0x18,0x00],
    '%': [0x00,0x66,0xAC,0xD8,0x36,0x6A,0xCC,0x00],
    '&': [0x38,0x6C,0x68,0x76,0xDC,0xCE,0x7B,0x00],
    "'": [0x18,0x18,0x30,0x00,0x00,0x00,0x00,0x00],
    '(': [0x0C,0x18,0x30,0x30,0x30,0x18,0x0C,0x00],
    ')': [0x30,0x18,0x0C,0x0C,0x0C,0x18,0x30,0x00],
    '*': [0x00,0x66,0x3C,0xFF,0x3C,0x66,0x00,0x00],
    '+': [0x00,0x18,0x18,0x7E,0x18,0x18,0x00,0x00],
    ',': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x30],
    '-': [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00],
    '.': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00],
    '/': [0x06,0x0C,0x18,0x30,0x60,0xC0,0x80,0x00],
    '0': [0x7C,0xC6,0xCE,0xD6,0xE6,0xC6,0x7C,0x00],
    '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
    '2': [0x7C,0xC6,0x06,0x1C,0x30,0x66,0xFE,0x00],
    '3': [0x7C,0xC6,0x06,0x3C,0x06,0xC6,0x7C,0x00],
    '4': [0x1C,0x3C,0x6C,0xCC,0xFE,0x0C,0x1E,0x00],
    '5': [0xFE,0xC0,0xC0,0xFC,0x06,0xC6,0x7C,0x00],
    '6': [0x38,0x60,0xC0,0xFC,0xC6,0xC6,0x7C,0x00],
    '7': [0xFE,0xC6,0x0C,0x18,0x30,0x30,0x30,0x00],
    '8': [0x7C,0xC6,0xC6,0x7C,0xC6,0xC6,0x7C,0x00],
    '9': [0x7C,0xC6,0xC6,0x7E,0x06,0x0C,0x78,0x00],
    ':': [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00],
    ';': [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x30],
    '<': [0x06,0x0C,0x18,0x30,0x18,0x0C,0x06,0x00],
    '=': [0x00,0x00,0x7E,0x00,0x00,0x7E,0x00,0x00],
    '>': [0x60,0x30,0x18,0x0C,0x18,0x30,0x60,0x00],
    '?': [0x7C,0xC6,0x0C,0x18,0x18,0x00,0x18,0x00],
    '@': [0x7C,0xC6,0xDE,0xDE,0xDE,0xC0,0x78,0x00],
    'A': [0x38,0x6C,0xC6,0xFE,0xC6,0xC6,0xC6,0x00],
    'B': [0xFC,0x66,0x66,0x7C,0x66,0x66,0xFC,0x00],
    'C': [0x3C,0x66,0xC0,0xC0,0xC0,0x66,0x3C,0x00],
    'D': [0xF8,0x6C,0x66,0x66,0x66,0x6C,0xF8,0x00],
    'E': [0xFE,0x62,0x68,0x78,0x68,0x62,0xFE,0x00],
    'F': [0xFE,0x62,0x68,0x78,0x68,0x60,0xF0,0x00],
    'G': [0x3C,0x66,0xC0,0xC0,0xCE,0x66,0x3A,0x00],
    'H': [0xC6,0xC6,0xC6,0xFE,0xC6,0xC6,0xC6,0x00],
    'I': [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
    'J': [0x1E,0x0C,0x0C,0x0C,0xCC,0xCC,0x78,0x00],
    'K': [0xE6,0x66,0x6C,0x78,0x6C,0x66,0xE6,0x00],
    'L': [0xF0,0x60,0x60,0x60,0x62,0x66,0xFE,0x00],
    'M': [0xC6,0xEE,0xFE,0xFE,0xD6,0xC6,0xC6,0x00],
    'N': [0xC6,0xE6,0xF6,0xDE,0xCE,0xC6,0xC6,0x00],
    'O': [0x7C,0xC6,0xC6,0xC6,0xC6,0xC6,0x7C,0x00],
    'P': [0xFC,0x66,0x66,0x7C,0x60,0x60,0xF0,0x00],
    'Q': [0x7C,0xC6,0xC6,0xC6,0xC6,0xCE,0x7C,0x0E],
    'R': [0xFC,0x66,0x66,0x7C,0x6C,0x66,0xE6,0x00],
    'S': [0x7C,0xC6,0x60,0x38,0x0C,0xC6,0x7C,0x00],
    'T': [0x7E,0x7E,0x5A,0x18,0x18,0x18,0x3C,0x00],
    'U': [0xC6,0xC6,0xC6,0xC6,0xC6,0xC6,0x7C,0x00],
    'V': [0xC6,0xC6,0xC6,0xC6,0xC6,0x6C,0x38,0x00],
    'W': [0xC6,0xC6,0xC6,0xD6,0xD6,0xFE,0x6C,0x00],
    'X': [0xC6,0xC6,0x6C,0x38,0x6C,0xC6,0xC6,0x00],
    'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x3C,0x00],
    'Z': [0xFE,0xC6,0x8C,0x18,0x32,0x66,0xFE,0x00],
    '[': [0x3C,0x30,0x30,0x30,0x30,0x30,0x3C,0x00],
    '\\': [0xC0,0x60,0x30,0x18,0x0C,0x06,0x02,0x00],
    ']': [0x3C,0x0C,0x0C,0x0C,0x0C,0x0C,0x3C,0x00],
    '^': [0x10,0x38,0x6C,0xC6,0x00,0x00,0x00,0x00],
    '_': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF],
    '`': [0x30,0x18,0x0C,0x00,0x00,0x00,0x00,0x00],
    'a': [0x00,0x00,0x78,0x0C,0x7C,0xCC,0x76,0x00],
    'b': [0xE0,0x60,0x7C,0x66,0x66,0x66,0xDC,0x00],
    'c': [0x00,0x00,0x7C,0xC6,0xC0,0xC6,0x7C,0x00],
    'd': [0x1C,0x0C,0x7C,0xCC,0xCC,0xCC,0x76,0x00],
    'e': [0x00,0x00,0x7C,0xC6,0xFE,0xC0,0x7C,0x00],
    'f': [0x3C,0x66,0x60,0xF8,0x60,0x60,0xF0,0x00],
    'g': [0x00,0x00,0x76,0xCC,0xCC,0x7C,0x0C,0xF8],
    'h': [0xE0,0x60,0x6C,0x76,0x66,0x66,0xE6,0x00],
    'i': [0x18,0x00,0x38,0x18,0x18,0x18,0x3C,0x00],
    'j': [0x06,0x00,0x0E,0x06,0x06,0x66,0x66,0x3C],
    'k': [0xE0,0x60,0x66,0x6C,0x78,0x6C,0xE6,0x00],
    'l': [0x38,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
    'm': [0x00,0x00,0xEC,0xFE,0xD6,0xD6,0xD6,0x00],
    'n': [0x00,0x00,0xDC,0x66,0x66,0x66,0x66,0x00],
    'o': [0x00,0x00,0x7C,0xC6,0xC6,0xC6,0x7C,0x00],
    'p': [0x00,0x00,0xDC,0x66,0x66,0x7C,0x60,0xF0],
    'q': [0x00,0x00,0x76,0xCC,0xCC,0x7C,0x0C,0x1E],
    'r': [0x00,0x00,0xDC,0x76,0x60,0x60,0xF0,0x00],
    's': [0x00,0x00,0x7E,0xC0,0x7C,0x06,0xFC,0x00],
    't': [0x30,0x30,0xFC,0x30,0x30,0x36,0x1C,0x00],
    'u': [0x00,0x00,0xCC,0xCC,0xCC,0xCC,0x76,0x00],
    'v': [0x00,0x00,0xC6,0xC6,0xC6,0x6C,0x38,0x00],
    'w': [0x00,0x00,0xC6,0xD6,0xD6,0xFE,0x6C,0x00],
    'x': [0x00,0x00,0xC6,0x6C,0x38,0x6C,0xC6,0x00],
    'y': [0x00,0x00,0xC6,0xC6,0xC6,0x7E,0x06,0xFC],
    'z': [0x00,0x00,0x7E,0x4C,0x18,0x32,0x7E,0x00],
    '{': [0x0E,0x18,0x18,0x70,0x18,0x18,0x0E,0x00],
    '|': [0x18,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
    '}': [0x70,0x18,0x18,0x0E,0x18,0x18,0x70,0x00],
    '~': [0x76,0xDC,0x00,0x00,0x00,0x00,0x00,0x00],
}

def draw_char(surface, char, x, y, color, scale=1):
    """Draw a single character using 8x8 bitmap font"""
    if char not in FONT_8X8:
        char = '?'
    bitmap = FONT_8X8[char]
    for row_idx, row in enumerate(bitmap):
        for col in range(8):
            if row & (0x80 >> col):
                px = x + col * scale
                py = y + row_idx * scale
                if scale == 1:
                    surface.set_at((px, py), color)
                else:
                    pygame.draw.rect(surface, color, (px, py, scale, scale))

def draw_text(surface, text, x, y, color, scale=1):
    """Draw text string"""
    cursor_x = x
    for char in text.upper():
        draw_char(surface, char, cursor_x, y, color, scale)
        cursor_x += 8 * scale

def get_text_width(text, scale=1):
    return len(text) * 8 * scale

# ============== UI DRAWING FUNCTIONS ==============

def draw_3d_rect(surface, rect, raised=True):
    """Draw NT-style 3D rectangle"""
    x, y, w, h = rect
    if raised:
        light = COLORS['window_light']
        dark = COLORS['window_shadow']
    else:
        light = COLORS['window_shadow']
        dark = COLORS['window_light']
    
    pygame.draw.rect(surface, COLORS['button_face'], rect)
    # Top and left (light)
    pygame.draw.line(surface, light, (x, y), (x + w - 1, y))
    pygame.draw.line(surface, light, (x, y), (x, y + h - 1))
    # Bottom and right (dark)
    pygame.draw.line(surface, dark, (x, y + h - 1), (x + w - 1, y + h - 1))
    pygame.draw.line(surface, dark, (x + w - 1, y), (x + w - 1, y + h - 1))

def draw_button(surface, rect, text, pressed=False):
    """Draw NT-style button"""
    draw_3d_rect(surface, rect, not pressed)
    text_w = get_text_width(text)
    text_x = rect[0] + (rect[2] - text_w) // 2
    text_y = rect[1] + (rect[3] - 8) // 2
    if pressed:
        text_x += 1
        text_y += 1
    draw_text(surface, text, text_x, text_y, COLORS['black'])

def draw_window(surface, rect, title, active=True):
    """Draw NT 1.0 style window"""
    x, y, w, h = rect
    
    # Window background
    pygame.draw.rect(surface, COLORS['window_bg'], rect)
    
    # 3D border
    pygame.draw.line(surface, COLORS['window_light'], (x, y), (x + w - 1, y))
    pygame.draw.line(surface, COLORS['window_light'], (x, y), (x, y + h - 1))
    pygame.draw.line(surface, COLORS['window_shadow'], (x, y + h - 1), (x + w - 1, y + h - 1))
    pygame.draw.line(surface, COLORS['window_shadow'], (x + w - 1, y), (x + w - 1, y + h - 1))
    pygame.draw.line(surface, COLORS['black'], (x + 1, y + h - 2), (x + w - 2, y + h - 2))
    pygame.draw.line(surface, COLORS['black'], (x + w - 2, y + 1), (x + w - 2, y + h - 2))
    
    # Title bar
    title_color = COLORS['title_active'] if active else COLORS['title_inactive']
    pygame.draw.rect(surface, title_color, (x + 3, y + 3, w - 6, 18))
    
    # Title text
    draw_text(surface, title, x + 24, y + 7, COLORS['title_text'])
    
    # System menu button
    draw_3d_rect(surface, (x + 5, y + 5, 14, 14), True)
    # Draw cat icon in system menu
    draw_cat_icon_mini(surface, x + 6, y + 6)
    
    # Minimize/Maximize/Close buttons
    btn_y = y + 5
    btn_x = x + w - 50
    draw_3d_rect(surface, (btn_x, btn_y, 14, 14), True)
    pygame.draw.line(surface, COLORS['black'], (btn_x + 3, btn_y + 10), (btn_x + 10, btn_y + 10))
    
    btn_x += 16
    draw_3d_rect(surface, (btn_x, btn_y, 14, 14), True)
    pygame.draw.rect(surface, COLORS['black'], (btn_x + 3, btn_y + 3, 8, 8), 1)
    
    btn_x += 16
    draw_3d_rect(surface, (btn_x, btn_y, 14, 14), True)
    pygame.draw.line(surface, COLORS['black'], (btn_x + 3, btn_y + 3), (btn_x + 10, btn_y + 10))
    pygame.draw.line(surface, COLORS['black'], (btn_x + 10, btn_y + 3), (btn_x + 3, btn_y + 10))

def draw_cat_icon_mini(surface, x, y):
    """Draw tiny cat face for system menu"""
    # Ears
    pygame.draw.polygon(surface, COLORS['cat_orange'], [(x+2, y+4), (x+4, y), (x+6, y+4)])
    pygame.draw.polygon(surface, COLORS['cat_orange'], [(x+6, y+4), (x+8, y), (x+10, y+4)])
    # Face
    pygame.draw.ellipse(surface, COLORS['cat_orange'], (x+1, y+3, 10, 9))
    # Eyes
    surface.set_at((x+4, y+6), COLORS['black'])
    surface.set_at((x+8, y+6), COLORS['black'])
    # Nose
    surface.set_at((x+6, y+8), COLORS['cat_pink'])

def draw_cat_icon(surface, x, y, size=32):
    """Draw cat face icon for desktop"""
    # Ears
    ear_h = size // 3
    pygame.draw.polygon(surface, COLORS['cat_orange'], 
        [(x + size//4, y + ear_h), (x + size//3, y), (x + size//2 - 2, y + ear_h)])
    pygame.draw.polygon(surface, COLORS['cat_orange'],
        [(x + size//2 + 2, y + ear_h), (x + size*2//3, y), (x + size*3//4, y + ear_h)])
    # Inner ears
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//3, y + ear_h - 2), (x + size//3 + 2, y + 4), (x + size//2 - 4, y + ear_h - 2)])
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//2 + 4, y + ear_h - 2), (x + size*2//3 - 2, y + 4), (x + size*2//3, y + ear_h - 2)])
    
    # Face
    pygame.draw.ellipse(surface, COLORS['cat_orange'], (x + 2, y + ear_h - 4, size - 4, size - ear_h + 4))
    
    # Eyes
    eye_y = y + size // 2
    pygame.draw.ellipse(surface, COLORS['black'], (x + size//4, eye_y - 3, 6, 8))
    pygame.draw.ellipse(surface, COLORS['black'], (x + size*3//4 - 6, eye_y - 3, 6, 8))
    # Eye highlights
    pygame.draw.circle(surface, COLORS['white'], (x + size//4 + 2, eye_y - 1), 2)
    pygame.draw.circle(surface, COLORS['white'], (x + size*3//4 - 4, eye_y - 1), 2)
    
    # Nose
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//2, eye_y + 6), (x + size//2 - 4, eye_y + 10), (x + size//2 + 4, eye_y + 10)])
    
    # Mouth
    pygame.draw.arc(surface, COLORS['black'], (x + size//2 - 8, eye_y + 8, 8, 6), 3.14, 0, 1)
    pygame.draw.arc(surface, COLORS['black'], (x + size//2, eye_y + 8, 8, 6), 3.14, 0, 1)
    
    # Whiskers
    for i in range(3):
        offset = (i - 1) * 3
        pygame.draw.line(surface, COLORS['black'], 
            (x + 4, eye_y + 10 + offset), (x - 4, eye_y + 8 + offset * 2))
        pygame.draw.line(surface, COLORS['black'],
            (x + size - 4, eye_y + 10 + offset), (x + size + 4, eye_y + 8 + offset * 2))

# ============== DESKTOP ICONS ==============

class DesktopIcon:
    def __init__(self, x, y, name, icon_type):
        self.x = x
        self.y = y
        self.name = name
        self.icon_type = icon_type
        self.selected = False
        self.width = 64
        self.height = 64
    
    def draw(self, surface):
        # Selection highlight
        if self.selected:
            pygame.draw.rect(surface, COLORS['selection'], 
                (self.x, self.y, self.width, self.height - 16))
        
        # Draw icon based on type
        icon_x = self.x + (self.width - 32) // 2
        icon_y = self.y + 4
        
        if self.icon_type == 'cat':
            draw_cat_icon(surface, icon_x, icon_y, 32)
        elif self.icon_type == 'folder':
            self.draw_folder_icon(surface, icon_x, icon_y)
        elif self.icon_type == 'file':
            self.draw_file_icon(surface, icon_x, icon_y)
        elif self.icon_type == 'terminal':
            self.draw_terminal_icon(surface, icon_x, icon_y)
        elif self.icon_type == 'trash':
            self.draw_trash_icon(surface, icon_x, icon_y)
        
        # Draw label
        label_color = COLORS['white'] if self.selected else COLORS['white']
        label_bg = COLORS['selection'] if self.selected else None
        
        text_w = get_text_width(self.name)
        text_x = self.x + (self.width - text_w) // 2
        text_y = self.y + 44
        
        if label_bg:
            pygame.draw.rect(surface, label_bg, (text_x - 2, text_y - 1, text_w + 4, 10))
        draw_text(surface, self.name, text_x, text_y, label_color)
    
    def draw_folder_icon(self, surface, x, y):
        # Folder tab
        pygame.draw.rect(surface, (255, 220, 100), (x, y + 4, 12, 6))
        # Folder body
        pygame.draw.rect(surface, (255, 200, 50), (x, y + 8, 32, 22))
        pygame.draw.rect(surface, COLORS['black'], (x, y + 8, 32, 22), 1)
    
    def draw_file_icon(self, surface, x, y):
        # Paper
        pygame.draw.rect(surface, COLORS['white'], (x + 4, y, 24, 30))
        pygame.draw.rect(surface, COLORS['black'], (x + 4, y, 24, 30), 1)
        # Folded corner
        pygame.draw.polygon(surface, COLORS['window_dark'], 
            [(x + 20, y), (x + 28, y + 8), (x + 20, y + 8)])
        # Lines
        for i in range(4):
            pygame.draw.line(surface, COLORS['window_dark'],
                (x + 8, y + 12 + i * 5), (x + 24, y + 12 + i * 5))
    
    def draw_terminal_icon(self, surface, x, y):
        # Terminal window
        pygame.draw.rect(surface, COLORS['black'], (x, y, 32, 30))
        pygame.draw.rect(surface, COLORS['window_dark'], (x, y, 32, 30), 1)
        # Prompt
        draw_text(surface, 'C:\\>', x + 2, y + 4, (0, 255, 0))
        draw_text(surface, '_', x + 26, y + 4, (0, 255, 0))
    
    def draw_trash_icon(self, surface, x, y):
        # Trash can
        pygame.draw.rect(surface, COLORS['window_dark'], (x + 4, y + 6, 24, 24))
        pygame.draw.rect(surface, COLORS['black'], (x + 4, y + 6, 24, 24), 1)
        # Lid
        pygame.draw.rect(surface, COLORS['window_dark'], (x + 2, y + 2, 28, 6))
        pygame.draw.rect(surface, COLORS['black'], (x + 2, y + 2, 28, 6), 1)
        # Handle
        pygame.draw.rect(surface, COLORS['window_dark'], (x + 12, y, 8, 4))
        pygame.draw.rect(surface, COLORS['black'], (x + 12, y, 8, 4), 1)
    
    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)

# ============== MAIN APPLICATION ==============

class CatOS:
    def __init__(self):
        self.state = 'boot'  # boot, desktop
        self.boot_start_time = None
        self.boot_phase = 0
        self.chime_played = False
        
        # Desktop icons
        self.icons = [
            DesktopIcon(20, 20, 'My Cat', 'cat'),
            DesktopIcon(20, 100, 'Files', 'folder'),
            DesktopIcon(20, 180, 'Docs', 'file'),
            DesktopIcon(20, 260, 'Terminal', 'terminal'),
            DesktopIcon(20, 340, 'Trash', 'trash'),
        ]
        
        # Windows
        self.windows = []
        self.show_start_menu = False
        
        # Clock
        self.clock = pygame.time.Clock()
    
    def run(self):
        running = True
        self.boot_start_time = time.time()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            if self.state == 'boot':
                self.draw_boot_screen()
            else:
                self.draw_desktop()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def draw_boot_screen(self):
        elapsed = time.time() - self.boot_start_time
        
        screen.fill((0, 0, 32))  # Dark blue boot screen
        
        if elapsed < 0.5:
            # Initial black
            screen.fill(COLORS['black'])
        elif elapsed < 1.5:
            # Logo fade in
            alpha = min(255, int((elapsed - 0.5) * 255))
            self.draw_boot_logo(alpha)
        elif elapsed < 2.0:
            # Play chime
            if not self.chime_played:
                play_boot_chime()
                self.chime_played = True
            self.draw_boot_logo(255)
        elif elapsed < 5.5:
            # Show logo with progress
            self.draw_boot_logo(255)
            self.draw_boot_progress(elapsed - 2.0)
        else:
            # Transition to desktop
            self.state = 'desktop'
    
    def draw_boot_logo(self, alpha):
        # Center position
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60
        
        # Draw large cat face
        size = 120
        x = cx - size // 2
        y = cy - size // 2
        
        # Background glow
        for r in range(60, 0, -5):
            glow_alpha = int(alpha * (60 - r) / 60 * 0.3)
            glow_color = (glow_alpha, glow_alpha // 2, glow_alpha)
            pygame.draw.circle(screen, glow_color, (cx, cy + 20), r + 60)
        
        # Large cat ears
        ear_h = size // 3
        pygame.draw.polygon(screen, COLORS['cat_orange'],
            [(x + size//4, y + ear_h), (x + size//3, y), (x + size//2 - 4, y + ear_h)])
        pygame.draw.polygon(screen, COLORS['cat_orange'],
            [(x + size//2 + 4, y + ear_h), (x + size*2//3, y), (x + size*3//4, y + ear_h)])
        
        # Inner ears
        pygame.draw.polygon(screen, COLORS['cat_pink'],
            [(x + size//3 + 4, y + ear_h - 4), (x + size//3 + 8, y + 12), (x + size//2 - 10, y + ear_h - 4)])
        pygame.draw.polygon(screen, COLORS['cat_pink'],
            [(x + size//2 + 10, y + ear_h - 4), (x + size*2//3 - 8, y + 12), (x + size*2//3 - 4, y + ear_h - 4)])
        
        # Face
        pygame.draw.ellipse(screen, COLORS['cat_orange'], (x + 4, y + ear_h - 10, size - 8, size - ear_h + 20))
        
        # Eyes
        eye_y = y + size // 2 + 10
        pygame.draw.ellipse(screen, COLORS['black'], (x + size//4, eye_y - 8, 20, 24))
        pygame.draw.ellipse(screen, COLORS['black'], (x + size*3//4 - 20, eye_y - 8, 20, 24))
        # Pupils/highlights
        pygame.draw.circle(screen, COLORS['white'], (x + size//4 + 6, eye_y - 2), 5)
        pygame.draw.circle(screen, COLORS['white'], (x + size*3//4 - 14, eye_y - 2), 5)
        
        # Nose
        pygame.draw.polygon(screen, COLORS['cat_pink'],
            [(cx, eye_y + 18), (cx - 10, eye_y + 28), (cx + 10, eye_y + 28)])
        
        # Mouth
        pygame.draw.arc(screen, COLORS['black'], (cx - 20, eye_y + 24, 20, 14), 3.14, 0, 2)
        pygame.draw.arc(screen, COLORS['black'], (cx, eye_y + 24, 20, 14), 3.14, 0, 2)
        
        # Whiskers
        for i in range(3):
            offset = (i - 1) * 8
            pygame.draw.line(screen, (180, 180, 180),
                (x + 10, eye_y + 30 + offset), (x - 30, eye_y + 25 + offset * 2), 1)
            pygame.draw.line(screen, (180, 180, 180),
                (x + size - 10, eye_y + 30 + offset), (x + size + 30, eye_y + 25 + offset * 2), 1)
        
        # Title
        title = "CAT OS 1.X"
        title_x = cx - get_text_width(title, 3) // 2
        draw_text(screen, title, title_x, cy + 100, COLORS['white'], 3)
        
        # Subtitle
        subtitle = "BY TEAM FLAMES / SAMSOFT"
        sub_x = cx - get_text_width(subtitle) // 2
        draw_text(screen, subtitle, sub_x, cy + 140, COLORS['window_dark'])
    
    def draw_boot_progress(self, elapsed):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 180
        
        # Progress bar background
        bar_width = 300
        bar_height = 20
        bar_x = cx - bar_width // 2
        
        pygame.draw.rect(screen, COLORS['window_shadow'], (bar_x - 2, cy - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, COLORS['black'], (bar_x, cy, bar_width, bar_height))
        
        # Progress fill
        progress = min(1.0, elapsed / 3.5)
        fill_width = int(bar_width * progress)
        
        # Gradient fill
        for i in range(fill_width):
            t = i / bar_width
            r = int(100 + 155 * t)
            g = int(150 + 105 * t)
            b = int(200 - 100 * t)
            pygame.draw.line(screen, (r, g, b), (bar_x + i, cy + 2), (bar_x + i, cy + bar_height - 2))
        
        # Status text
        messages = ["Starting Cat OS...", "Loading drivers...", "Initializing meow engine...", 
                    "Calibrating purr modules...", "Welcome!"]
        msg_idx = min(int(progress * len(messages)), len(messages) - 1)
        msg = messages[msg_idx]
        msg_x = cx - get_text_width(msg) // 2
        draw_text(screen, msg, msg_x, cy + 30, COLORS['window_dark'])
    
    def draw_desktop(self):
        # Desktop background
        screen.fill(COLORS['desktop'])
        
        # Draw icons
        for icon in self.icons:
            icon.draw(screen)
        
        # Draw windows
        for window in self.windows:
            self.draw_window_content(window)
        
        # Draw taskbar
        self.draw_taskbar()
        
        # Draw start menu if open
        if self.show_start_menu:
            self.draw_start_menu()
    
    def draw_taskbar(self):
        # Taskbar background
        taskbar_rect = (0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32)
        draw_3d_rect(screen, taskbar_rect, True)
        
        # Start button
        start_rect = (4, SCREEN_HEIGHT - 28, 60, 24)
        draw_button(screen, start_rect, 'START', self.show_start_menu)
        
        # Draw cat icon on start button
        draw_cat_icon_mini(screen, 8, SCREEN_HEIGHT - 26)
        
        # Clock area
        clock_rect = (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 28, 66, 24)
        draw_3d_rect(screen, clock_rect, False)
        
        now = datetime.now()
        time_str = now.strftime('%H:%M')
        draw_text(screen, time_str, SCREEN_WIDTH - 58, SCREEN_HEIGHT - 22, COLORS['black'])
    
    def draw_start_menu(self):
        menu_x = 4
        menu_y = SCREEN_HEIGHT - 32 - 180
        menu_w = 160
        menu_h = 180
        
        # Menu background
        pygame.draw.rect(screen, COLORS['window_bg'], (menu_x, menu_y, menu_w, menu_h))
        draw_3d_rect(screen, (menu_x, menu_y, menu_w, menu_h), True)
        
        # Blue sidebar
        pygame.draw.rect(screen, COLORS['title_active'], (menu_x + 3, menu_y + 3, 24, menu_h - 6))
        
        # Sidebar text (vertical)
        sidebar_text = "CAT OS 1.X"
        for i, char in enumerate(sidebar_text):
            draw_text(screen, char, menu_x + 8, menu_y + menu_h - 20 - i * 12, COLORS['title_text'])
        
        # Menu items
        items = ['Programs', 'Documents', 'Settings', 'Find', 'Help', 'Run...', 'Shut Down']
        item_y = menu_y + 8
        for item in items:
            draw_text(screen, item, menu_x + 32, item_y, COLORS['black'])
            item_y += 24
    
    def draw_window_content(self, window):
        draw_window(screen, window['rect'], window['title'], window.get('active', True))
        
        # Content area
        x, y, w, h = window['rect']
        content_rect = (x + 4, y + 24, w - 8, h - 28)
        pygame.draw.rect(screen, COLORS['white'], content_rect)
        
        if window.get('content'):
            lines = window['content'].split('\n')
            for i, line in enumerate(lines[:10]):
                draw_text(screen, line, x + 8, y + 28 + i * 12, COLORS['black'])
    
    def handle_click(self, pos, button):
        if self.state != 'desktop':
            return
        
        mx, my = pos
        
        # Check start button
        if 4 <= mx <= 64 and SCREEN_HEIGHT - 28 <= my <= SCREEN_HEIGHT - 4:
            self.show_start_menu = not self.show_start_menu
            return
        
        # Close start menu if clicking elsewhere
        if self.show_start_menu:
            self.show_start_menu = False
        
        # Check icons
        for icon in self.icons:
            if icon.contains_point(mx, my):
                # Deselect others
                for other in self.icons:
                    other.selected = False
                icon.selected = True
                
                # Double click would open
                if button == 1:
                    self.open_icon(icon)
                return
        
        # Deselect all if clicking empty space
        for icon in self.icons:
            icon.selected = False
    
    def open_icon(self, icon):
        """Open a window for the icon"""
        content = ""
        title = icon.name
        
        if icon.icon_type == 'cat':
            title = "My Cat"
            content = "Name: Whiskers\nBreed: Tabby\nAge: 3 years\nFavorite: Naps\n\nMeow! :3"
        elif icon.icon_type == 'folder':
            title = "File Manager"
            content = "C:\\\n  CATOS\n  SYSTEM\n  USERS\n  PROGRAMS"
        elif icon.icon_type == 'terminal':
            title = "CAT-DOS Prompt"
            content = "Cat OS [Version 1.X]\n(C) Team Flames\n\nC:\\>"
        elif icon.icon_type == 'file':
            title = "Documents"
            content = "README.TXT\nNOTES.TXT\nMEOW.CAT"
        elif icon.icon_type == 'trash':
            title = "Recycle Bin"
            content = "(Empty)\n\nNo deleted items"
        
        # Create window
        win_x = 150 + len(self.windows) * 30
        win_y = 50 + len(self.windows) * 30
        
        self.windows.append({
            'rect': (win_x, win_y, 320, 200),
            'title': title,
            'content': content,
            'active': True
        })
        
        # Only keep last 3 windows
        if len(self.windows) > 3:
            self.windows.pop(0)

# ============== ENTRY POINT ==============

if __name__ == '__main__':
    print("=" * 50)
    print("  CAT OS 1.X - Windows NT 1.0 Style")
    print("  By Team Flames / Samsoft")
    print("=" * 50)
    print("\nStarting Cat OS...")
    print("Press ESC to exit\n")
    
    os = CatOS()
    os.run()
