#!/usr/bin/env python3
"""
Pixa - pygame版 AIピクセルアート生成アプリケーション (シンプルバージョン)
pygame-guiを使わずに純粋なpygameで実装
"""

import pygame
import sys
import os
import requests
import json
import threading
import time
import math
from io import BytesIO
import base64
from PIL import Image

# 定数
WINDOW_SIZE = (1400, 900)
SIDEBAR_WIDTH = 400
COLORS = {
    'bg': (25, 25, 35),
    'sidebar': (35, 35, 45),
    'button': (65, 105, 225),
    'button_hover': (85, 125, 245),
    'button_active': (45, 85, 205),
    'text': (255, 255, 255),
    'text_dim': (200, 200, 200),
    'panel': (45, 45, 55),
    'accent': (138, 43, 226),
    'input': (55, 55, 65),
    'input_active': (65, 65, 75),
    'slider': (100, 100, 110),
    'slider_handle': (150, 150, 160)
}

class Button:
    def __init__(self, x, y, width, height, text, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
    
    def draw(self, screen, font):
        color = COLORS['button_active'] if self.pressed else (COLORS['button_hover'] if self.hovered else COLORS['button'])
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        text_surface = font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
    
    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        
    def draw(self, screen, font):
        # スライダーバー
        pygame.draw.rect(screen, COLORS['slider'], self.rect, border_radius=3)
        
        # ハンドル
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + ratio * self.rect.width
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
        pygame.draw.rect(screen, COLORS['slider_handle'], handle_rect, border_radius=5)
        
        # ラベルと値
        if self.label:
            label_text = f"{self.label}: {self.val:.1f}" if isinstance(self.val, float) else f"{self.label}: {int(self.val)}"
            text_surface = font.render(label_text, True, COLORS['text'])
            screen.blit(text_surface, (self.rect.x, self.rect.y - 25))

class TextInput:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen, font):
        color = COLORS['input_active'] if self.active else COLORS['input']
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        pygame.draw.rect(screen, COLORS['text_dim'], self.rect, 1, border_radius=3)
        
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['text'] if self.text else COLORS['text_dim']
        
        text_surface = font.render(display_text, True, text_color)
        text_rect = pygame.Rect(self.rect.x + 10, self.rect.y, self.rect.width - 20, self.rect.height)
        screen.blit(text_surface, (text_rect.x, text_rect.centery - text_surface.get_height() // 2))
        
        # カーソル
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.x + font.size(self.text)[0]
            pygame.draw.line(screen, COLORS['text'], 
                           (cursor_x, text_rect.y + 5), 
                           (cursor_x, text_rect.bottom - 5), 2)

class PixaApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Pixa - AI Pixel Art Generator")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # フォント（日本語対応）
        try:
            # macOSのシステムフォントを使用
            self.font = pygame.font.SysFont('hiragino sans', 24)
            self.title_font = pygame.font.SysFont('hiragino sans', 36)
            self.small_font = pygame.font.SysFont('hiragino sans', 18)
        except:
            # フォールバック
            try:
                self.font = pygame.font.SysFont('arial unicode ms', 24)
                self.title_font = pygame.font.SysFont('arial unicode ms', 36)
                self.small_font = pygame.font.SysFont('arial unicode ms', 18)
            except:
                # 最終フォールバック
                self.font = pygame.font.Font(None, 24)
                self.title_font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 18)
        
        # 状態管理
        self.current_image = None
        self.generating = False
        self.server_status = "Connecting..."
        
        # API設定
        self.api_url = "http://localhost:5001"
        
        self.setup_ui()
        self.check_server_status()
        
    def setup_ui(self):
        """UIコンポーネントを設定"""
        y_offset = 50
        
        # プロンプト入力
        self.prompt_input = TextInput(20, y_offset, SIDEBAR_WIDTH-40, 35, "Enter prompt...")
        y_offset += 55
        
        # ネガティブプロンプト
        self.negative_prompt_input = TextInput(20, y_offset, SIDEBAR_WIDTH-40, 35, "Negative prompt")
        y_offset += 75
        
        # スライダー
        self.width_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 256, 1024, 512, "Width")
        y_offset += 50
        
        self.height_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 256, 1024, 512, "Height")
        y_offset += 50
        
        self.pixel_size_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 2, 20, 8, "Pixel Size")
        y_offset += 50
        
        self.palette_size_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 4, 64, 16, "Palette Size")
        y_offset += 50
        
        self.steps_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 10, 50, 20, "Steps")
        y_offset += 50
        
        self.guidance_slider = Slider(20, y_offset, SIDEBAR_WIDTH-40, 20, 1.0, 20.0, 7.5, "Guidance")
        y_offset += 75
        
        # シード入力
        self.seed_input = TextInput(20, y_offset, SIDEBAR_WIDTH-40, 35, "Seed (empty for random)")
        y_offset += 55
        
        # 生成ボタン
        self.generate_button = Button(20, y_offset, SIDEBAR_WIDTH-40, 50, "Generate Pixel Art", self.generate_image)
        y_offset += 70
        
        # 保存ボタン
        self.save_button = Button(20, y_offset, (SIDEBAR_WIDTH-50)//2, 40, "Save", self.save_image)
        
        # クイックプロンプトボタン
        quick_prompts = [
            "cute cat", "brave knight", "dragon", "castle", "spaceship"
        ]
        
        self.quick_buttons = []
        y_offset += 60
        for i, prompt in enumerate(quick_prompts):
            button = Button(20, y_offset + i * 45, SIDEBAR_WIDTH-40, 35, prompt, 
                          lambda p=prompt: self.set_prompt(p))
            self.quick_buttons.append(button)
    
    def set_prompt(self, prompt):
        """クイックプロンプトを設定"""
        self.prompt_input.text = prompt
    
    def check_server_status(self):
        """サーバーステータスをチェック"""
        def check():
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                data = response.json()
                if data.get('status') == 'healthy' and data.get('pipeline_loaded'):
                    self.server_status = "Connected successfully"
                else:
                    self.server_status = "Loading model..."
            except Exception as e:
                self.server_status = f"Connection error: {str(e)[:50]}"
        
        threading.Thread(target=check, daemon=True).start()
    
    def generate_image(self):
        """画像生成を実行"""
        if self.generating:
            return
            
        prompt = self.prompt_input.text.strip()
        if not prompt or prompt == self.prompt_input.placeholder:
            self.server_status = "Please enter a prompt"
            return
        
        self.generating = True
        self.server_status = "Generating..."
        
        def generate():
            try:
                params = {
                    'prompt': prompt,
                    'negative_prompt': self.negative_prompt_input.text if self.negative_prompt_input.text != self.negative_prompt_input.placeholder else "",
                    'width': int(self.width_slider.val),
                    'height': int(self.height_slider.val),
                    'pixel_size': int(self.pixel_size_slider.val),
                    'palette_size': int(self.palette_size_slider.val),
                    'steps': int(self.steps_slider.val),
                    'guidance_scale': self.guidance_slider.val,
                    'seed': int(self.seed_input.text) if self.seed_input.text.isdigit() else None
                }
                
                response = requests.post(
                    f"{self.api_url}/generate",
                    json=params,
                    timeout=120
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('success'):
                        # Base64画像をPygame surfaceに変換
                        image_data = data['image'].split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        pil_image = Image.open(BytesIO(image_bytes))
                        
                        # PILからPygameへの変換
                        mode = pil_image.mode
                        size = pil_image.size
                        raw = pil_image.tobytes()
                        
                        pygame_image = pygame.image.fromstring(raw, size, mode)
                        
                        self.current_image = pygame_image
                        self.server_status = "Generation complete"
                    else:
                        self.server_status = f"Error: {data.get('error', 'Unknown error')}"
                else:
                    self.server_status = f"HTTP Error: {response.status_code}"
                    
            except Exception as e:
                self.server_status = f"Generation Error: {str(e)[:50]}"
            finally:
                self.generating = False
        
        threading.Thread(target=generate, daemon=True).start()
    
    def save_image(self):
        """画像を保存"""
        if self.current_image:
            timestamp = int(time.time())
            filename = f"pixel_art_{timestamp}.png"
            pygame.image.save(self.current_image, filename)
            self.server_status = f"Saved: {filename}"
        else:
            self.server_status = "No image to save"
    
    def handle_events(self):
        """イベント処理"""
        dt = self.clock.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # キーボードショートカット
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_RETURN and keys[pygame.K_LCTRL]:
                    self.generate_image()
                elif event.key == pygame.K_s and keys[pygame.K_LCTRL]:
                    self.save_image()
            
            # UI要素のイベント処理
            self.prompt_input.handle_event(event)
            self.negative_prompt_input.handle_event(event)
            self.seed_input.handle_event(event)
            
            self.width_slider.handle_event(event)
            self.height_slider.handle_event(event)
            self.pixel_size_slider.handle_event(event)
            self.palette_size_slider.handle_event(event)
            self.steps_slider.handle_event(event)
            self.guidance_slider.handle_event(event)
            
            self.generate_button.handle_event(event)
            self.save_button.handle_event(event)
            
            for button in self.quick_buttons:
                button.handle_event(event)
        
        # 更新
        self.prompt_input.update(dt)
        self.negative_prompt_input.update(dt)
        self.seed_input.update(dt)
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill(COLORS['bg'])
        
        # サイドバー
        pygame.draw.rect(self.screen, COLORS['sidebar'], (0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1]))
        
        # タイトル
        title_text = self.title_font.render("Pixa - AI Pixel Art", True, COLORS['accent'])
        self.screen.blit(title_text, (20, 10))
        
        # メイン表示エリア
        main_rect = pygame.Rect(SIDEBAR_WIDTH, 0, WINDOW_SIZE[0] - SIDEBAR_WIDTH, WINDOW_SIZE[1])
        pygame.draw.rect(self.screen, COLORS['panel'], main_rect)
        
        # 画像表示
        if self.current_image:
            # 画像をメインエリアの中央に配置
            image_rect = self.current_image.get_rect()
            
            # アスペクト比を保持してリサイズ
            max_width = main_rect.width - 40
            max_height = main_rect.height - 40
            
            scale_x = max_width / image_rect.width
            scale_y = max_height / image_rect.height
            scale = min(scale_x, scale_y, 1.0)  # 1.0を超えない
            
            if scale < 1.0:
                new_width = int(image_rect.width * scale)
                new_height = int(image_rect.height * scale)
                scaled_image = pygame.transform.scale(self.current_image, (new_width, new_height))
            else:
                scaled_image = self.current_image
                new_width, new_height = image_rect.size
            
            # 中央配置
            x = SIDEBAR_WIDTH + (main_rect.width - new_width) // 2
            y = (main_rect.height - new_height) // 2
            
            self.screen.blit(scaled_image, (x, y))
            
            # 画像情報表示
            info_text = f"{image_rect.width}x{image_rect.height}px"
            info_surface = self.small_font.render(info_text, True, COLORS['text_dim'])
            self.screen.blit(info_surface, (x, y + new_height + 10))
        else:
            # プレースホルダー
            placeholder_text = self.font.render("Generated image will appear here", True, COLORS['text_dim'])
            text_rect = placeholder_text.get_rect(center=main_rect.center)
            self.screen.blit(placeholder_text, text_rect)
        
        # UI要素描画
        self.prompt_input.draw(self.screen, self.font)
        self.negative_prompt_input.draw(self.screen, self.font)
        self.seed_input.draw(self.screen, self.font)
        
        self.width_slider.draw(self.screen, self.small_font)
        self.height_slider.draw(self.screen, self.small_font)
        self.pixel_size_slider.draw(self.screen, self.small_font)
        self.palette_size_slider.draw(self.screen, self.small_font)
        self.steps_slider.draw(self.screen, self.small_font)
        self.guidance_slider.draw(self.screen, self.small_font)
        
        self.generate_button.draw(self.screen, self.font)
        self.save_button.draw(self.screen, self.font)
        
        for button in self.quick_buttons:
            button.draw(self.screen, self.small_font)
        
        # ステータス表示
        status_color = COLORS['accent'] if "complete" in self.server_status or "Saved" in self.server_status else COLORS['text_dim']
        status_text = self.small_font.render(f"Status: {self.server_status}", True, status_color)
        self.screen.blit(status_text, (10, WINDOW_SIZE[1] - 25))
        
        # 操作説明
        help_text = "Ctrl+Enter: Generate | Ctrl+S: Save"
        help_surface = self.small_font.render(help_text, True, COLORS['text_dim'])
        self.screen.blit(help_surface, (SIDEBAR_WIDTH + 20, WINDOW_SIZE[1] - 25))
        
        pygame.display.flip()
    
    def run(self):
        """メインループ"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """エントリーポイント"""
    app = PixaApp()
    app.run()

if __name__ == "__main__":
    main()