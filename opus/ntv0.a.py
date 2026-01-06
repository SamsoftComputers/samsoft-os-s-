#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CAT OS 1.X - Windows NT Style OS                          ║
║                         By Team Flames / Samsoft                             ║
║                   FULLY FIXED - All Buttons Working!                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
- Draggable windows with working minimize/maximize/close buttons
- Working Start Menu with all items clickable
- Desktop icons with double-click to open
- Taskbar with running apps
- Cool boot animation with Vista-style chime
- Multiple apps: Terminal, Notepad, Calculator, Cat Facts, Settings
"""

import pygame
import pygame.gfxdraw
import math
import random
import struct
import time
from datetime import datetime

pygame.init()
AUDIO_AVAILABLE = False
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except:
    print("Audio not available - running without sound")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cat OS 1.X - Team Flames")

# NT 1.0 Color Palette
COLORS = {
    'desktop': (0, 128, 128),
    'window_bg': (192, 192, 192),
    'window_dark': (128, 128, 128),
    'window_light': (255, 255, 255),
    'window_shadow': (64, 64, 64),
    'title_active': (0, 0, 128),
    'title_inactive': (128, 128, 128),
    'title_text': (255, 255, 255),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'button_face': (192, 192, 192),
    'button_hover': (210, 210, 210),
    'button_pressed': (160, 160, 160),
    'menu_bar': (192, 192, 192),
    'menu_hover': (0, 0, 128),
    'selection': (0, 0, 128),
    'cat_orange': (255, 165, 0),
    'cat_pink': (255, 182, 193),
    'red': (200, 50, 50),
    'green': (50, 200, 50),
    'blue': (50, 50, 200),
}

# ============== PROCEDURAL AUDIO ==============
def generate_sine_wave(freq, duration, volume=0.3, sample_rate=44100):
    samples = int(sample_rate * duration)
    wave = []
    for i in range(samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * freq * t) * volume
        wave.append(value)
    return wave

def generate_envelope(samples, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
    total = len(samples)
    envelope = []
    attack_samples = int(total * attack)
    decay_samples = int(total * decay)
    release_samples = int(total * release)
    sustain_samples = total - attack_samples - decay_samples - release_samples
    
    for i in range(attack_samples):
        envelope.append(i / max(1, attack_samples))
    for i in range(decay_samples):
        envelope.append(1.0 - (1.0 - sustain) * (i / max(1, decay_samples)))
    for i in range(max(0, sustain_samples)):
        envelope.append(sustain)
    for i in range(release_samples):
        envelope.append(sustain * (1.0 - i / max(1, release_samples)))
    
    while len(envelope) < total:
        envelope.append(0)
    
    return [samples[i] * envelope[i] for i in range(min(len(samples), len(envelope)))]

def mix_waves(*waves):
    max_len = max(len(w) for w in waves) if waves else 0
    result = [0.0] * max_len
    for wave in waves:
        for i, sample in enumerate(wave):
            result[i] += sample
    max_val = max(abs(s) for s in result) if result else 1
    if max_val == 0:
        max_val = 1
    return [s / max_val * 0.8 for s in result]

def generate_vista_chime():
    sample_rate = 44100
    pad_g = generate_envelope(generate_sine_wave(196.00, 3.5, 0.15), 0.3, 0.1, 0.5, 0.3)
    pad_b = generate_envelope(generate_sine_wave(246.94, 3.5, 0.12), 0.35, 0.1, 0.5, 0.3)
    pad_d = generate_envelope(generate_sine_wave(293.66, 3.5, 0.12), 0.4, 0.1, 0.5, 0.3)
    pad_a = generate_envelope(generate_sine_wave(220.00, 3.5, 0.08), 0.45, 0.1, 0.5, 0.3)
    
    def bell_tone(freq, start_time, duration=0.8):
        wave = generate_sine_wave(freq, duration, 0.25)
        h2 = generate_sine_wave(freq * 2, duration, 0.1)
        h3 = generate_sine_wave(freq * 3, duration, 0.05)
        combined = mix_waves(wave, h2, h3)
        combined = generate_envelope(combined, 0.01, 0.15, 0.3, 0.54)
        silence_before = [0.0] * int(sample_rate * start_time)
        return silence_before + combined
    
    melody1 = bell_tone(392.00, 0.0, 0.9)
    melody2 = bell_tone(493.88, 0.4, 0.9)
    melody3 = bell_tone(587.33, 0.8, 0.9)
    melody4 = bell_tone(783.99, 1.2, 1.2)
    
    sub = generate_envelope(generate_sine_wave(98.00, 3.0, 0.1), 0.5, 0.1, 0.3, 0.3)
    
    final = mix_waves(pad_g, pad_b, pad_d, pad_a, melody1, melody2, melody3, melody4, sub)
    
    stereo_data = []
    for sample in final:
        val = int(sample * 32767)
        val = max(-32768, min(32767, val))
        stereo_data.append(struct.pack('<hh', val, val))
    
    return b''.join(stereo_data)

def generate_click_sound():
    sample_rate = 44100
    wave = generate_sine_wave(800, 0.05, 0.3)
    wave = generate_envelope(wave, 0.01, 0.1, 0.2, 0.69)
    stereo_data = []
    for sample in wave:
        val = int(sample * 32767)
        val = max(-32768, min(32767, val))
        stereo_data.append(struct.pack('<hh', val, val))
    return b''.join(stereo_data)

def play_boot_chime():
    if not AUDIO_AVAILABLE:
        return None
    try:
        chime_data = generate_vista_chime()
        sound = pygame.mixer.Sound(buffer=chime_data)
        sound.play()
        return sound
    except:
        return None

def play_click():
    if not AUDIO_AVAILABLE:
        return
    try:
        click_data = generate_click_sound()
        sound = pygame.mixer.Sound(buffer=click_data)
        sound.set_volume(0.3)
        sound.play()
    except:
        pass

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
    if char not in FONT_8X8:
        char = '?'
    bitmap = FONT_8X8.get(char, FONT_8X8['?'])
    for row_idx, row in enumerate(bitmap):
        for col in range(8):
            if row & (0x80 >> col):
                px = x + col * scale
                py = y + row_idx * scale
                if scale == 1:
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        surface.set_at((px, py), color)
                else:
                    pygame.draw.rect(surface, color, (px, py, scale, scale))

def draw_text(surface, text, x, y, color, scale=1):
    cursor_x = x
    for char in text.upper():
        draw_char(surface, char, cursor_x, y, color, scale)
        cursor_x += 8 * scale

def get_text_width(text, scale=1):
    return len(text) * 8 * scale

# ============== UI COMPONENTS ==============

def draw_3d_rect(surface, rect, raised=True):
    x, y, w, h = rect
    light = COLORS['window_light'] if raised else COLORS['window_shadow']
    dark = COLORS['window_shadow'] if raised else COLORS['window_light']
    
    pygame.draw.rect(surface, COLORS['button_face'], rect)
    pygame.draw.line(surface, light, (x, y), (x + w - 1, y))
    pygame.draw.line(surface, light, (x, y), (x, y + h - 1))
    pygame.draw.line(surface, dark, (x, y + h - 1), (x + w - 1, y + h - 1))
    pygame.draw.line(surface, dark, (x + w - 1, y), (x + w - 1, y + h - 1))

def draw_cat_icon_mini(surface, x, y):
    pygame.draw.polygon(surface, COLORS['cat_orange'], [(x+2, y+4), (x+4, y), (x+6, y+4)])
    pygame.draw.polygon(surface, COLORS['cat_orange'], [(x+6, y+4), (x+8, y), (x+10, y+4)])
    pygame.draw.ellipse(surface, COLORS['cat_orange'], (x+1, y+3, 10, 9))
    surface.set_at((x+4, y+6), COLORS['black'])
    surface.set_at((x+8, y+6), COLORS['black'])
    surface.set_at((x+6, y+8), COLORS['cat_pink'])

def draw_cat_icon(surface, x, y, size=32):
    ear_h = size // 3
    pygame.draw.polygon(surface, COLORS['cat_orange'], 
        [(x + size//4, y + ear_h), (x + size//3, y), (x + size//2 - 2, y + ear_h)])
    pygame.draw.polygon(surface, COLORS['cat_orange'],
        [(x + size//2 + 2, y + ear_h), (x + size*2//3, y), (x + size*3//4, y + ear_h)])
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//3, y + ear_h - 2), (x + size//3 + 2, y + 4), (x + size//2 - 4, y + ear_h - 2)])
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//2 + 4, y + ear_h - 2), (x + size*2//3 - 2, y + 4), (x + size*2//3, y + ear_h - 2)])
    pygame.draw.ellipse(surface, COLORS['cat_orange'], (x + 2, y + ear_h - 4, size - 4, size - ear_h + 4))
    eye_y = y + size // 2
    pygame.draw.ellipse(surface, COLORS['black'], (x + size//4, eye_y - 3, 6, 8))
    pygame.draw.ellipse(surface, COLORS['black'], (x + size*3//4 - 6, eye_y - 3, 6, 8))
    pygame.draw.circle(surface, COLORS['white'], (x + size//4 + 2, eye_y - 1), 2)
    pygame.draw.circle(surface, COLORS['white'], (x + size*3//4 - 4, eye_y - 1), 2)
    pygame.draw.polygon(surface, COLORS['cat_pink'],
        [(x + size//2, eye_y + 6), (x + size//2 - 4, eye_y + 10), (x + size//2 + 4, eye_y + 10)])
    pygame.draw.arc(surface, COLORS['black'], (x + size//2 - 8, eye_y + 8, 8, 6), 3.14, 0, 1)
    pygame.draw.arc(surface, COLORS['black'], (x + size//2, eye_y + 8, 8, 6), 3.14, 0, 1)
    for i in range(3):
        offset = (i - 1) * 3
        pygame.draw.line(surface, COLORS['black'], 
            (x + 4, eye_y + 10 + offset), (x - 4, eye_y + 8 + offset * 2))
        pygame.draw.line(surface, COLORS['black'],
            (x + size - 4, eye_y + 10 + offset), (x + size + 4, eye_y + 8 + offset * 2))

# ============== WINDOW CLASS ==============

class Window:
    def __init__(self, x, y, w, h, title, content="", app_type="default"):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.content = content
        self.app_type = app_type
        self.active = True
        self.minimized = False
        self.maximized = False
        self.dragging = False
        self.drag_offset = (0, 0)
        self.prev_rect = None
        
        self.input_text = ""
        self.calc_display = "0"
        self.calc_value = 0
        self.calc_op = None
        self.terminal_history = ["Cat OS [Version 1.X]", "(C) Team Flames", "", "C:\\>"]
        self.terminal_input = ""
    
    def get_title_bar_rect(self):
        return pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.w - 6, 18)
    
    def get_close_btn_rect(self):
        return pygame.Rect(self.rect.x + self.rect.w - 19, self.rect.y + 5, 14, 14)
    
    def get_max_btn_rect(self):
        return pygame.Rect(self.rect.x + self.rect.w - 35, self.rect.y + 5, 14, 14)
    
    def get_min_btn_rect(self):
        return pygame.Rect(self.rect.x + self.rect.w - 51, self.rect.y + 5, 14, 14)
    
    def draw(self, surface):
        if self.minimized:
            return
        
        x, y, w, h = self.rect
        
        pygame.draw.rect(surface, COLORS['window_bg'], self.rect)
        pygame.draw.line(surface, COLORS['window_light'], (x, y), (x + w - 1, y))
        pygame.draw.line(surface, COLORS['window_light'], (x, y), (x, y + h - 1))
        pygame.draw.line(surface, COLORS['window_shadow'], (x, y + h - 1), (x + w - 1, y + h - 1))
        pygame.draw.line(surface, COLORS['window_shadow'], (x + w - 1, y), (x + w - 1, y + h - 1))
        pygame.draw.line(surface, COLORS['black'], (x + 1, y + h - 2), (x + w - 2, y + h - 2))
        pygame.draw.line(surface, COLORS['black'], (x + w - 2, y + 1), (x + w - 2, y + h - 2))
        
        title_color = COLORS['title_active'] if self.active else COLORS['title_inactive']
        pygame.draw.rect(surface, title_color, (x + 3, y + 3, w - 6, 18))
        draw_text(surface, self.title[:25], x + 24, y + 7, COLORS['title_text'])
        
        draw_3d_rect(surface, (x + 5, y + 5, 14, 14), True)
        draw_cat_icon_mini(surface, x + 6, y + 6)
        
        min_rect = self.get_min_btn_rect()
        draw_3d_rect(surface, min_rect, True)
        pygame.draw.line(surface, COLORS['black'], (min_rect.x + 3, min_rect.y + 10), (min_rect.x + 10, min_rect.y + 10))
        
        max_rect = self.get_max_btn_rect()
        draw_3d_rect(surface, max_rect, True)
        if self.maximized:
            pygame.draw.rect(surface, COLORS['black'], (max_rect.x + 2, max_rect.y + 5, 6, 6), 1)
            pygame.draw.rect(surface, COLORS['black'], (max_rect.x + 5, max_rect.y + 2, 6, 6), 1)
        else:
            pygame.draw.rect(surface, COLORS['black'], (max_rect.x + 3, max_rect.y + 3, 8, 8), 1)
        
        close_rect = self.get_close_btn_rect()
        draw_3d_rect(surface, close_rect, True)
        pygame.draw.line(surface, COLORS['black'], (close_rect.x + 3, close_rect.y + 3), (close_rect.x + 10, close_rect.y + 10))
        pygame.draw.line(surface, COLORS['black'], (close_rect.x + 10, close_rect.y + 3), (close_rect.x + 3, close_rect.y + 10))
        
        content_rect = pygame.Rect(x + 4, y + 24, w - 8, h - 28)
        pygame.draw.rect(surface, COLORS['white'], content_rect)
        pygame.draw.rect(surface, COLORS['window_shadow'], content_rect, 1)
        
        self.draw_content(surface, content_rect)
    
    def draw_content(self, surface, content_rect):
        x, y, w, h = content_rect
        
        if self.app_type == "terminal":
            pygame.draw.rect(surface, COLORS['black'], content_rect)
            for i, line in enumerate(self.terminal_history[-12:]):
                draw_text(surface, line, x + 4, y + 4 + i * 12, (0, 255, 0))
            input_line = f"C:\\>{self.terminal_input}_"
            draw_text(surface, input_line, x + 4, y + 4 + len(self.terminal_history[-12:]) * 12, (0, 255, 0))
            
        elif self.app_type == "calculator":
            pygame.draw.rect(surface, (200, 220, 200), (x + 10, y + 10, w - 20, 30))
            pygame.draw.rect(surface, COLORS['black'], (x + 10, y + 10, w - 20, 30), 1)
            draw_text(surface, self.calc_display[-15:], x + w - 25 - get_text_width(self.calc_display[-15:]), y + 18, COLORS['black'])
            
            buttons = [['7', '8', '9', '/'], ['4', '5', '6', '*'], ['1', '2', '3', '-'], ['C', '0', '=', '+']]
            btn_w, btn_h = 40, 30
            start_x, start_y = x + 15, y + 50
            for row_i, row in enumerate(buttons):
                for col_i, label in enumerate(row):
                    bx = start_x + col_i * (btn_w + 5)
                    by = start_y + row_i * (btn_h + 5)
                    draw_3d_rect(surface, (bx, by, btn_w, btn_h), True)
                    draw_text(surface, label, bx + btn_w//2 - 4, by + btn_h//2 - 4, COLORS['black'])
                    
        elif self.app_type == "notepad":
            lines = self.input_text.split('\n')
            for i, line in enumerate(lines[-15:]):
                draw_text(surface, line[:35], x + 4, y + 4 + i * 12, COLORS['black'])
            cursor_y = min(len(lines) - 1, 14)
            cursor_x = len(lines[-1]) if lines else 0
            if int(time.time() * 2) % 2:
                draw_text(surface, "_", x + 4 + cursor_x * 8, y + 4 + cursor_y * 12, COLORS['black'])
                
        elif self.app_type == "catfacts":
            facts = ["Cats sleep 12-16 hours daily!", "A cat's purr vibrates at",
                    "25-150 Hz - healing frequency!", "", "Cats have 230 bones.",
                    "Dogs only have 206!", "", "A group of cats is called",
                    "a 'clowder' :3", "", "Cats can rotate their ears", "180 degrees! Amazing!"]
            for i, line in enumerate(facts[:12]):
                color = COLORS['cat_orange'] if i in [0, 4, 7, 10] else COLORS['black']
                draw_text(surface, line, x + 8, y + 8 + i * 14, color)
                
        elif self.app_type == "settings":
            draw_text(surface, "CAT OS SETTINGS", x + 8, y + 8, COLORS['title_active'])
            draw_text(surface, "================", x + 8, y + 20, COLORS['black'])
            settings = ["[X] Enable meow sounds", "[X] Show cat cursor", "[ ] Dark mode",
                       "[X] Desktop icons", "", "Wallpaper: Teal", "Theme: Classic NT",
                       "", "Version: 1.X", "Build: MEOW-2025"]
            for i, line in enumerate(settings):
                draw_text(surface, line, x + 8, y + 36 + i * 14, COLORS['black'])
        else:
            lines = self.content.split('\n')
            for i, line in enumerate(lines[:12]):
                draw_text(surface, line, x + 8, y + 8 + i * 14, COLORS['black'])
    
    def handle_click(self, pos):
        if self.minimized:
            return None
        mx, my = pos
        
        if self.get_close_btn_rect().collidepoint(mx, my):
            play_click()
            return 'close'
        
        if self.get_max_btn_rect().collidepoint(mx, my):
            play_click()
            if self.maximized:
                if self.prev_rect:
                    self.rect = self.prev_rect.copy()
                self.maximized = False
            else:
                self.prev_rect = self.rect.copy()
                self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 32)
                self.maximized = True
            return 'maximize'
        
        if self.get_min_btn_rect().collidepoint(mx, my):
            play_click()
            self.minimized = True
            return 'minimize'
        
        if self.get_title_bar_rect().collidepoint(mx, my) and not self.maximized:
            self.dragging = True
            self.drag_offset = (mx - self.rect.x, my - self.rect.y)
            return 'drag'
        
        if self.app_type == "calculator":
            content_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 24, self.rect.w - 8, self.rect.h - 28)
            buttons = [['7', '8', '9', '/'], ['4', '5', '6', '*'], ['1', '2', '3', '-'], ['C', '0', '=', '+']]
            btn_w, btn_h = 40, 30
            start_x, start_y = content_rect.x + 15, content_rect.y + 50
            for row_i, row in enumerate(buttons):
                for col_i, label in enumerate(row):
                    bx = start_x + col_i * (btn_w + 5)
                    by = start_y + row_i * (btn_h + 5)
                    if pygame.Rect(bx, by, btn_w, btn_h).collidepoint(mx, my):
                        play_click()
                        self.calc_button(label)
                        return 'calc_btn'
        return 'click'
    
    def calc_button(self, btn):
        if btn.isdigit():
            self.calc_display = btn if self.calc_display == "0" else self.calc_display + btn
        elif btn == 'C':
            self.calc_display, self.calc_value, self.calc_op = "0", 0, None
        elif btn in ['+', '-', '*', '/']:
            self.calc_value, self.calc_op, self.calc_display = float(self.calc_display), btn, "0"
        elif btn == '=':
            try:
                current = float(self.calc_display)
                ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b, '*': lambda a,b: a*b, '/': lambda a,b: a/b if b else 0}
                result = ops.get(self.calc_op, lambda a,b: b)(self.calc_value, current)
                self.calc_display = str(int(result) if result == int(result) else round(result, 4))
                self.calc_op = None
            except:
                self.calc_display = "Error"
    
    def handle_key(self, event):
        if self.app_type == "terminal":
            if event.key == pygame.K_RETURN:
                cmd = self.terminal_input.strip().lower()
                self.terminal_history.append(f"C:\\>{self.terminal_input}")
                cmds = {'help': ["Commands: DIR, CLS, VER,", "MEOW, CAT, TIME, EXIT"],
                       'cls': 'clear', 'dir': ["CATOS    <DIR>", "SYSTEM   <DIR>", "MEOW.EXE  1337"],
                       'ver': ["Cat OS [Version 1.X]"], 'meow': ["MEOW! :3 ~nya~"],
                       'cat': ["  /\\_/\\", " ( o.o )", "  > ^ <"],
                       'time': [datetime.now().strftime("%H:%M:%S")], 'exit': 'close'}
                if cmd in cmds:
                    if cmds[cmd] == 'clear':
                        self.terminal_history = []
                    elif cmds[cmd] == 'close':
                        return 'close'
                    else:
                        self.terminal_history.extend(cmds[cmd])
                elif cmd:
                    self.terminal_history.append(f"'{cmd}' not recognized")
                self.terminal_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.terminal_input = self.terminal_input[:-1]
            elif event.unicode.isprintable():
                self.terminal_input += event.unicode
        elif self.app_type == "notepad":
            if event.key == pygame.K_RETURN:
                self.input_text += '\n'
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.unicode.isprintable():
                self.input_text += event.unicode
        return None

# ============== DESKTOP ICON ==============

class DesktopIcon:
    def __init__(self, x, y, name, icon_type, app_type="default"):
        self.x, self.y = x, y
        self.name, self.icon_type, self.app_type = name, icon_type, app_type
        self.selected = False
        self.width, self.height = 64, 64
        self.last_click = 0
    
    def draw(self, surface):
        if self.selected:
            pygame.draw.rect(surface, COLORS['selection'], (self.x, self.y, self.width, self.height - 16))
        
        icon_x, icon_y = self.x + (self.width - 32) // 2, self.y + 4
        
        if self.icon_type == 'cat':
            draw_cat_icon(surface, icon_x, icon_y, 32)
        elif self.icon_type == 'folder':
            pygame.draw.rect(surface, (255, 220, 100), (icon_x, icon_y + 4, 12, 6))
            pygame.draw.rect(surface, (255, 200, 50), (icon_x, icon_y + 8, 32, 22))
            pygame.draw.rect(surface, COLORS['black'], (icon_x, icon_y + 8, 32, 22), 1)
        elif self.icon_type == 'file':
            pygame.draw.rect(surface, COLORS['white'], (icon_x + 4, icon_y, 24, 30))
            pygame.draw.rect(surface, COLORS['black'], (icon_x + 4, icon_y, 24, 30), 1)
            pygame.draw.polygon(surface, COLORS['window_dark'], [(icon_x + 20, icon_y), (icon_x + 28, icon_y + 8), (icon_x + 20, icon_y + 8)])
            for i in range(4):
                pygame.draw.line(surface, COLORS['window_dark'], (icon_x + 8, icon_y + 12 + i * 5), (icon_x + 24, icon_y + 12 + i * 5))
        elif self.icon_type == 'terminal':
            pygame.draw.rect(surface, COLORS['black'], (icon_x, icon_y, 32, 30))
            pygame.draw.rect(surface, COLORS['window_dark'], (icon_x, icon_y, 32, 30), 1)
            draw_text(surface, 'C:\\>', icon_x + 2, icon_y + 4, (0, 255, 0))
        elif self.icon_type == 'trash':
            pygame.draw.rect(surface, COLORS['window_dark'], (icon_x + 4, icon_y + 6, 24, 24))
            pygame.draw.rect(surface, COLORS['black'], (icon_x + 4, icon_y + 6, 24, 24), 1)
            pygame.draw.rect(surface, COLORS['window_dark'], (icon_x + 2, icon_y + 2, 28, 6))
            pygame.draw.rect(surface, COLORS['black'], (icon_x + 2, icon_y + 2, 28, 6), 1)
            pygame.draw.rect(surface, COLORS['window_dark'], (icon_x + 12, icon_y, 8, 4))
        elif self.icon_type == 'calc':
            pygame.draw.rect(surface, (200, 200, 220), (icon_x + 2, icon_y, 28, 32))
            pygame.draw.rect(surface, COLORS['black'], (icon_x + 2, icon_y, 28, 32), 1)
            pygame.draw.rect(surface, (180, 200, 180), (icon_x + 5, icon_y + 3, 22, 10))
            for i in range(3):
                for j in range(3):
                    pygame.draw.rect(surface, COLORS['white'], (icon_x + 5 + j * 8, icon_y + 16 + i * 5, 6, 4))
        elif self.icon_type == 'notepad':
            pygame.draw.rect(surface, (255, 255, 200), (icon_x + 2, icon_y, 28, 32))
            pygame.draw.rect(surface, COLORS['black'], (icon_x + 2, icon_y, 28, 32), 1)
            for i in range(6):
                pygame.draw.line(surface, (200, 200, 200), (icon_x + 5, icon_y + 5 + i * 5), (icon_x + 27, icon_y + 5 + i * 5))
        
        text_w = get_text_width(self.name)
        text_x, text_y = self.x + (self.width - text_w) // 2, self.y + 44
        if self.selected:
            pygame.draw.rect(surface, COLORS['selection'], (text_x - 2, text_y - 1, text_w + 4, 10))
        draw_text(surface, self.name, text_x, text_y, COLORS['white'])
    
    def contains_point(self, px, py):
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
    
    def handle_click(self):
        now = time.time()
        double_click = (now - self.last_click) < 0.4
        self.last_click = now
        return double_click

# ============== MAIN OS CLASS ==============

class CatOS:
    def __init__(self):
        self.state = 'boot'
        self.boot_start_time = None
        self.chime_played = False
        
        self.icons = [
            DesktopIcon(20, 20, 'My Cat', 'cat', 'catfacts'),
            DesktopIcon(20, 100, 'Files', 'folder', 'default'),
            DesktopIcon(20, 180, 'Notepad', 'notepad', 'notepad'),
            DesktopIcon(20, 260, 'Terminal', 'terminal', 'terminal'),
            DesktopIcon(20, 340, 'Calc', 'calc', 'calculator'),
            DesktopIcon(20, 420, 'Trash', 'trash', 'default'),
            DesktopIcon(100, 20, 'Settings', 'file', 'settings'),
        ]
        
        self.windows = []
        self.show_start_menu = False
        self.start_menu_hover = -1
        self.clock = pygame.time.Clock()
        self.dragging_window = None
    
    def run(self):
        running = True
        self.boot_start_time = time.time()
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.windows:
                            self.windows.pop()
                        else:
                            running = False
                    elif self.windows and self.windows[-1].active:
                        result = self.windows[-1].handle_key(event)
                        if result == 'close':
                            self.windows.pop()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(mouse_pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging_window:
                        self.dragging_window.dragging = False
                        self.dragging_window = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_window and self.dragging_window.dragging:
                        dx, dy = self.dragging_window.drag_offset
                        self.dragging_window.rect.x = mouse_pos[0] - dx
                        self.dragging_window.rect.y = max(0, mouse_pos[1] - dy)
            
            if self.show_start_menu:
                self.update_start_menu_hover(mouse_pos)
            
            if self.state == 'boot':
                self.draw_boot_screen()
            else:
                self.draw_desktop()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def handle_click(self, pos, button):
        if self.state != 'desktop':
            return
        mx, my = pos
        
        if 4 <= mx <= 64 and SCREEN_HEIGHT - 28 <= my <= SCREEN_HEIGHT - 4:
            play_click()
            self.show_start_menu = not self.show_start_menu
            return
        
        if self.show_start_menu:
            menu_x, menu_y = 4, SCREEN_HEIGHT - 32 - 200
            menu_w, menu_h = 180, 200
            if menu_x <= mx <= menu_x + menu_w and menu_y <= my <= menu_y + menu_h:
                item_idx = (my - menu_y - 8) // 26
                if 0 <= item_idx < 7:
                    play_click()
                    self.handle_start_menu_click(item_idx)
                    self.show_start_menu = False
                    return
            else:
                self.show_start_menu = False
        
        taskbar_x = 70
        for win in self.windows:
            if win.minimized:
                btn_rect = pygame.Rect(taskbar_x, SCREEN_HEIGHT - 28, 100, 24)
                if btn_rect.collidepoint(mx, my):
                    play_click()
                    win.minimized = False
                    win.active = True
                    self.windows.remove(win)
                    self.windows.append(win)
                    return
                taskbar_x += 105
        
        for win in reversed(self.windows):
            if not win.minimized and win.rect.collidepoint(mx, my):
                result = win.handle_click(pos)
                if result == 'close':
                    self.windows.remove(win)
                elif result == 'drag':
                    self.dragging_window = win
                elif result:
                    for w in self.windows:
                        w.active = False
                    win.active = True
                    self.windows.remove(win)
                    self.windows.append(win)
                return
        
        for icon in self.icons:
            if icon.contains_point(mx, my):
                for other in self.icons:
                    other.selected = False
                icon.selected = True
                if icon.handle_click():
                    self.open_app(icon.name, icon.app_type)
                return
        
        for icon in self.icons:
            icon.selected = False
    
    def update_start_menu_hover(self, pos):
        mx, my = pos
        menu_x, menu_y = 4, SCREEN_HEIGHT - 32 - 200
        if menu_x + 30 <= mx <= menu_x + 180 and menu_y + 8 <= my <= menu_y + 190:
            self.start_menu_hover = (my - menu_y - 8) // 26
        else:
            self.start_menu_hover = -1
    
    def handle_start_menu_click(self, idx):
        apps = [('Terminal', 'terminal'), ('Documents', 'default'), ('Settings', 'settings'),
                ('Calculator', 'calculator'), ('Cat Facts', 'catfacts'), ('Terminal', 'terminal'), None]
        if idx == 6:
            pygame.quit()
            exit()
        elif apps[idx]:
            self.open_app(*apps[idx])
    
    def open_app(self, name, app_type):
        content, title, w, h = "", name, 320, 240
        configs = {
            'catfacts': ("Cat Facts :3", 280, 220),
            'terminal': ("CAT-DOS Prompt", 400, 300),
            'calculator': ("Calculator", 200, 220),
            'notepad': ("Notepad", 350, 280),
            'settings': ("Settings", 280, 250),
        }
        if app_type in configs:
            title, w, h = configs[app_type]
        elif name == 'Documents':
            content = "C:\\\n  README.TXT\n  NOTES.TXT\n  MEOW.CAT"
        elif name == 'Trash':
            content = "(Empty)\n\nNo deleted items."
        
        offset = len([w for w in self.windows if not w.minimized]) * 25
        for win in self.windows:
            win.active = False
        self.windows.append(Window(150 + offset, 50 + offset, w, h, title, content, app_type))
    
    def draw_boot_screen(self):
        elapsed = time.time() - self.boot_start_time
        if elapsed < 0.5:
            screen.fill(COLORS['black'])
        elif elapsed < 2.0:
            if elapsed >= 1.5 and not self.chime_played:
                play_boot_chime()
                self.chime_played = True
            screen.fill((0, 0, 32))
            self.draw_boot_logo()
        elif elapsed < 5.0:
            screen.fill((0, 0, 32))
            self.draw_boot_logo()
            self.draw_boot_progress(elapsed - 2.0)
        else:
            self.state = 'desktop'
    
    def draw_boot_logo(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60
        size, x, y = 120, cx - 60, cy - 60
        
        for r in range(60, 0, -5):
            glow = int((60 - r) / 60 * 50)
            pygame.draw.circle(screen, (glow, glow // 2, glow), (cx, cy + 20), r + 60)
        
        ear_h = size // 3
        pygame.draw.polygon(screen, COLORS['cat_orange'], [(x + size//4, y + ear_h), (x + size//3, y), (x + size//2 - 4, y + ear_h)])
        pygame.draw.polygon(screen, COLORS['cat_orange'], [(x + size//2 + 4, y + ear_h), (x + size*2//3, y), (x + size*3//4, y + ear_h)])
        pygame.draw.polygon(screen, COLORS['cat_pink'], [(x + size//3 + 4, y + ear_h - 4), (x + size//3 + 8, y + 12), (x + size//2 - 10, y + ear_h - 4)])
        pygame.draw.polygon(screen, COLORS['cat_pink'], [(x + size//2 + 10, y + ear_h - 4), (x + size*2//3 - 8, y + 12), (x + size*2//3 - 4, y + ear_h - 4)])
        pygame.draw.ellipse(screen, COLORS['cat_orange'], (x + 4, y + ear_h - 10, size - 8, size - ear_h + 20))
        
        eye_y = y + size // 2 + 10
        pygame.draw.ellipse(screen, COLORS['black'], (x + size//4, eye_y - 8, 20, 24))
        pygame.draw.ellipse(screen, COLORS['black'], (x + size*3//4 - 20, eye_y - 8, 20, 24))
        pygame.draw.circle(screen, COLORS['white'], (x + size//4 + 6, eye_y - 2), 5)
        pygame.draw.circle(screen, COLORS['white'], (x + size*3//4 - 14, eye_y - 2), 5)
        pygame.draw.polygon(screen, COLORS['cat_pink'], [(cx, eye_y + 18), (cx - 10, eye_y + 28), (cx + 10, eye_y + 28)])
        pygame.draw.arc(screen, COLORS['black'], (cx - 20, eye_y + 24, 20, 14), 3.14, 0, 2)
        pygame.draw.arc(screen, COLORS['black'], (cx, eye_y + 24, 20, 14), 3.14, 0, 2)
        
        for i in range(3):
            offset = (i - 1) * 8
            pygame.draw.line(screen, (180, 180, 180), (x + 10, eye_y + 30 + offset), (x - 30, eye_y + 25 + offset * 2), 1)
            pygame.draw.line(screen, (180, 180, 180), (x + size - 10, eye_y + 30 + offset), (x + size + 30, eye_y + 25 + offset * 2), 1)
        
        title = "CAT OS 1.X"
        draw_text(screen, title, cx - get_text_width(title, 3) // 2, cy + 100, COLORS['white'], 3)
        subtitle = "BY TEAM FLAMES / SAMSOFT"
        draw_text(screen, subtitle, cx - get_text_width(subtitle) // 2, cy + 140, COLORS['window_dark'])
    
    def draw_boot_progress(self, elapsed):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180
        bar_width, bar_height = 300, 20
        bar_x = cx - bar_width // 2
        
        pygame.draw.rect(screen, COLORS['window_shadow'], (bar_x - 2, cy - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, COLORS['black'], (bar_x, cy, bar_width, bar_height))
        
        progress = min(1.0, elapsed / 3.0)
        for i in range(int(bar_width * progress)):
            t = i / bar_width
            pygame.draw.line(screen, (int(100 + 155 * t), int(150 + 105 * t), int(200 - 100 * t)), (bar_x + i, cy + 2), (bar_x + i, cy + bar_height - 2))
        
        messages = ["Starting Cat OS...", "Loading drivers...", "Initializing meow...", "Calibrating purr...", "Welcome!"]
        msg = messages[min(int(progress * len(messages)), len(messages) - 1)]
        draw_text(screen, msg, cx - get_text_width(msg) // 2, cy + 30, COLORS['window_dark'])
    
    def draw_desktop(self):
        screen.fill(COLORS['desktop'])
        for icon in self.icons:
            icon.draw(screen)
        for win in self.windows:
            win.draw(screen)
        self.draw_taskbar()
        if self.show_start_menu:
            self.draw_start_menu()
    
    def draw_taskbar(self):
        draw_3d_rect(screen, (0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32), True)
        
        draw_3d_rect(screen, (4, SCREEN_HEIGHT - 28, 60, 24), not self.show_start_menu)
        draw_cat_icon_mini(screen, 8, SCREEN_HEIGHT - 26)
        offset = 1 if self.show_start_menu else 0
        draw_text(screen, 'START', 22 + offset, SCREEN_HEIGHT - 22 + offset, COLORS['black'])
        
        btn_x = 70
        for win in self.windows:
            btn_pressed = win.active and not win.minimized
            draw_3d_rect(screen, (btn_x, SCREEN_HEIGHT - 28, 100, 24), not btn_pressed)
            draw_text(screen, win.title[:10], btn_x + 4, SCREEN_HEIGHT - 22, COLORS['black'])
            btn_x += 105
        
        draw_3d_rect(screen, (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 28, 66, 24), False)
        draw_text(screen, datetime.now().strftime('%H:%M'), SCREEN_WIDTH - 58, SCREEN_HEIGHT - 22, COLORS['black'])
    
    def draw_start_menu(self):
        menu_x, menu_y, menu_w, menu_h = 4, SCREEN_HEIGHT - 32 - 200, 180, 200
        pygame.draw.rect(screen, COLORS['window_bg'], (menu_x, menu_y, menu_w, menu_h))
        draw_3d_rect(screen, (menu_x, menu_y, menu_w, menu_h), True)
        pygame.draw.rect(screen, COLORS['title_active'], (menu_x + 3, menu_y + 3, 24, menu_h - 6))
        
        for i, char in enumerate("CAT OS 1.X"):
            draw_text(screen, char, menu_x + 8, menu_y + menu_h - 20 - i * 14, COLORS['title_text'])
        
        items = ['Programs', 'Documents', 'Settings', 'Calculator', 'Help', 'Run...', 'Shut Down']
        item_y = menu_y + 8
        for i, item in enumerate(items):
            if i == self.start_menu_hover:
                pygame.draw.rect(screen, COLORS['selection'], (menu_x + 30, item_y - 2, menu_w - 34, 22))
                draw_text(screen, item, menu_x + 34, item_y + 2, COLORS['white'])
            else:
                draw_text(screen, item, menu_x + 34, item_y + 2, COLORS['black'])
            if i == 5:
                pygame.draw.line(screen, COLORS['window_shadow'], (menu_x + 30, item_y - 6), (menu_x + menu_w - 4, item_y - 6))
            item_y += 26

if __name__ == '__main__':
    print("=" * 50)
    print("  CAT OS 1.X - Windows NT Style")
    print("  By Team Flames / Samsoft - FULLY FIXED")
    print("=" * 50)
    print("\nFeatures: Draggable windows, working buttons,")
    print("Start menu, Terminal, Calculator, Notepad")
    print("Press ESC to close windows/exit\n")
    CatOS().run()
