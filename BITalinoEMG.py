# coding: utf_8

import numpy as np
from bitalino import BITalino

import pygame
import pygame.mixer
from pygame.locals import *
import sys

# ----------------------------------------
# デバイスの初期化

macAddress = "20:16:12:21:35:82" # MACアドレス
samplingRate = 1000 # サンプリングレート
acqChannels = [0] # 取得チャネル（A1）
nSamples = 100 # 取得サンプル数

device = BITalino(macAddress) # デバイスの取得
print(device.version())
device.start(samplingRate, acqChannels) # データ取得開始
# ----------------------------------------

# ----------------------------------------
# 信号の取得

def selected():
    BITS = 10 # 信号のビット幅
    VCC = 3.3 # 操作電圧
    GAIN = 1009 # センサーゲイン
    THRESHOLD = 0.3 # 閾値

    data = device.read(nSamples)
    emg = (((((data[:,5] / 2**BITS) - 1/2) * VCC) / GAIN) * 1000) # 単位変換（mV）
    emg = np.abs(emg) # 絶対値
    max_value = np.max(emg)
    print(max_value)

    if max_value > THRESHOLD:
        return True
    else:
        return False
# ----------------------------------------

# ----------------------------------------
# PyGameの初期化

pygame.init()
width = 1920 # 幅
height = 1080 # 高さ
pygame.display.set_caption("BITalino EMG")
screen = pygame.display.set_mode((width, height))
# ----------------------------------------

# ----------------------------------------
# 色の設定
BLACK = (0 ,0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
# ----------------------------------------

# ----------------------------------------
# フォントの設定
font = pygame.font.Font("font/ipaexg.ttf", 50)
surfaces = []
labels = ["はい", "いいえ", "トイレ", "ほしい", "痛い", "食べたい", "飲みたい", "わからない", "やめて"]
for label in labels:
    surface = font.render(label, False, BLACK)
    surfaces.append(surface)
# ----------------------------------------

# ----------------------------------------
# サウンドの設定

pygame.mixer.init()
sounds = []
wavs = ["hai.wav", "iie.wav", "toire.wav", "hosii.wav", "itai.wav", "tabetai.wav", "nomitai.wav", "wakaranai.wav", "yamete.wav"]
for wav in wavs:
    sound = pygame.mixer.Sound("sound/" + wav)
    sounds.append(sound)
# ----------------------------------------

# ----------------------------------------
# 選択ボックスの初期化

size_x = 3
unit_x = (width / size_x)
size_y = 3
unit_y = (height / size_y)
boxes = []

for x in range(0, 3):
    for y in range(0, 3):
        left = x * unit_x
        top = y * unit_y
        box = pygame.Rect(left, top, unit_x, unit_y)
        boxes.append(box)
# ----------------------------------------

# ----------------------------------------
# メインループ
target = 0
time = pygame.time.get_ticks()

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            device.stop()
            device.close()
            sys.exit()

    if (pygame.time.get_ticks() - time) >= 1000:
        target = (target + 1) % (size_x * size_y)
        time = pygame.time.get_ticks()

    index = 0
    for box in boxes:
        if index == target:
            if selected():
                pygame.draw.rect(screen, RED, box)
                if not(pygame.mixer.get_busy()):
                    sounds[target].play()
            else:
                pygame.draw.rect(screen, YELLOW, box)
        else:
            pygame.draw.rect(screen, WHITE, box)

        pygame.draw.rect(screen, BLACK, box, 1) #枠線
        index += 1

    for surface, box in zip(surfaces, boxes):
        x = box.x + (box.width / 2) - (surface.get_width() / 2)
        y = box.y + (box.height / 2) - (surface.get_height() / 2)
        screen.blit(surface, (x, y))

    pygame.display.flip()
# ----------------------------------------
