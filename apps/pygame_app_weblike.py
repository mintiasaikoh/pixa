#!/usr/bin/env python3
"""
Pixa - pygame版 AIピクセルアート生成アプリケーション
元のWebUIスタイルを再現
"""

import pygame
# pygame.freetypeは使わずに標準のpygame.fontを使用
import sys
import os
import requests
import json
import threading
import time
from io import BytesIO
import base64
from PIL import Image

# 定数 - WebUIと同じカラーパレット
WINDOW_SIZE = (1400, 900)
SIDEBAR_WIDTH = 380
COLORS = {
    'dark_bg': (26, 26, 26),        # #1a1a1a
    'darker_bg': (13, 13, 13),      # #0d0d0d  
    'sidebar_bg': (45, 45, 45),     # #2d2d2d
    'input_bg': (51, 51, 51),       # #333
    'input_border': (85, 85, 85),   # #555
    'pixel_primary': (0, 255, 65),  # #00ff41
    'pixel_secondary': (255, 0, 128), # #ff0080
    'text_white': (255, 255, 255),
    'text_gray': (153, 153, 153),   # #999
    'text_light': (200, 200, 200),
    'button_disabled': (102, 102, 102), # #666
}

class SimpleButton:
    def __init__(self, x, y, width, height, text, callback=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.hovered = False
        self.pressed = False
        
    def handle_event(self, event):
        if not self.enabled:
            return
            
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
        if not self.enabled:
            bg_color = COLORS['button_disabled']
            text_color = COLORS['text_gray']
        elif self.pressed:
            bg_color = (0, 204, 51)  # darker green
            text_color = COLORS['dark_bg']
        elif self.hovered:
            bg_color = (0, 204, 51)  # darker green
            text_color = COLORS['dark_bg']
        else:
            bg_color = COLORS['pixel_primary']
            text_color = COLORS['dark_bg']
            
        pygame.draw.rect(screen, bg_color, self.rect)
        
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class SimpleSlider:
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
        # スライダートラック
        pygame.draw.rect(screen, COLORS['input_border'], self.rect)
        
        # 進行バー
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        progress_width = ratio * self.rect.width
        progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
        pygame.draw.rect(screen, COLORS['pixel_primary'], progress_rect)
        
        # つまみ
        thumb_x = self.rect.x + progress_width - 8
        thumb_rect = pygame.Rect(thumb_x, self.rect.y - 4, 16, self.rect.height + 8)
        pygame.draw.rect(screen, COLORS['pixel_primary'], thumb_rect)

class SimpleTextArea:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = None
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.text += '\n'
            elif event.unicode and len(event.unicode) > 0:
                # すべての文字（日本語含む）を受け付ける
                if ord(event.unicode) >= 32 or event.unicode == '\t':
                    self.text += event.unicode
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen, font):
        # 背景とボーダー
        pygame.draw.rect(screen, COLORS['input_bg'], self.rect)
        border_color = COLORS['pixel_primary'] if self.active else COLORS['input_border']
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # テキスト表示エリア
        text_rect = pygame.Rect(self.rect.x + 8, self.rect.y + 8, 
                               self.rect.width - 16, self.rect.height - 16)
        
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['text_white'] if self.text else COLORS['text_gray']
        
        # 複数行対応
        lines = display_text.split('\n')
        y_offset = 0
        line_height = font.get_height() + 2
        
        for line in lines:
            if y_offset + line_height > text_rect.height:
                break
            if line:  # 空行でない場合
                text_surface = font.render(line, True, text_color)
                screen.blit(text_surface, (text_rect.x, text_rect.y + y_offset))
            y_offset += line_height
        
        # カーソル表示
        if self.active and self.cursor_visible:
            cursor_lines = self.text.split('\n')
            cursor_line = len(cursor_lines) - 1
            cursor_x = text_rect.x
            if cursor_lines[-1]:
                cursor_x += font.size(cursor_lines[-1])[0]
            cursor_y = text_rect.y + cursor_line * line_height
            
            if cursor_y < text_rect.bottom - line_height:
                pygame.draw.line(screen, COLORS['text_white'], 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + line_height), 2)

class PixaApp:
    def __init__(self):
        pygame.init()
        
        # フォント設定
        try:
            # Courier New風のフォント
            self.font = pygame.font.SysFont("courier", 14)
            self.title_font = pygame.font.SysFont("courier", 20)
            self.label_font = pygame.font.SysFont("courier", 12)
        except:
            self.font = pygame.font.Font(None, 14)
            self.title_font = pygame.font.Font(None, 20)
            self.label_font = pygame.font.Font(None, 12)
        
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Pixa - AI Pixel Art Generator")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 状態管理
        self.current_image = None
        self.generating = False
        self.server_status = "Connecting..."
        
        # API設定
        self.api_url = "http://localhost:5001"
        
        self.setup_ui()
        self.check_server_status()
        
    def setup_ui(self):
        """WebUIライクなUIを設定"""
        x_margin = 20
        y_pos = 60
        input_width = SIDEBAR_WIDTH - x_margin * 2
        
        # プロンプト入力
        self.prompt_input = SimpleTextArea(
            x_margin, y_pos, input_width, 80, 
            "例: 可愛い猫の戦士が森にいる (日本語OK!)"
        )
        y_pos += 100
        
        # ネガティブプロンプト
        self.negative_prompt_input = SimpleTextArea(
            x_margin, y_pos, input_width, 50, 
            "blurry, low quality, bad anatomy"
        )
        y_pos += 80
        
        # 画像サイズ選択
        self.width_options = [256, 512, 768]
        self.height_options = [256, 512, 768]
        self.selected_width = 1  # 512px
        self.selected_height = 1  # 512px
        
        # サイズボタン
        button_width = (input_width - 10) // 2
        self.width_buttons = []
        for i, size in enumerate(self.width_options):
            btn = SimpleButton(x_margin + i * 30, y_pos + 25, 60, 25, f"{size}", 
                             lambda w=i: self.set_width(w))
            self.width_buttons.append(btn)
        
        self.height_buttons = []
        for i, size in enumerate(self.height_options):
            btn = SimpleButton(x_margin + button_width + 10 + i * 30, y_pos + 25, 60, 25, f"{size}", 
                             lambda h=i: self.set_height(h))
            self.height_buttons.append(btn)
        y_pos += 80
        
        # スライダー
        self.pixel_size_slider = SimpleSlider(x_margin, y_pos + 20, input_width, 20, 2, 16, 8, "Pixel Size")
        y_pos += 60
        
        self.palette_size_slider = SimpleSlider(x_margin, y_pos + 20, input_width, 20, 4, 64, 16, "Palette Size")
        y_pos += 60
        
        self.steps_slider = SimpleSlider(x_margin, y_pos + 20, input_width, 20, 10, 50, 20, "Steps")
        y_pos += 60
        
        self.guidance_slider = SimpleSlider(x_margin, y_pos + 20, input_width, 20, 1.0, 20.0, 7.5, "Guidance")
        y_pos += 80
        
        # シード入力
        self.seed_input = SimpleTextArea(x_margin, y_pos, input_width, 40, "Seed (空白でランダム)")
        y_pos += 60
        
        # 生成ボタン
        self.generate_button = SimpleButton(x_margin, y_pos, input_width, 50, 
                                          "GENERATE PIXEL ART", self.generate_image)
        y_pos += 70
        
        # 保存ボタン
        self.save_button = SimpleButton(x_margin, y_pos, input_width, 40, 
                                      "SAVE IMAGE", self.save_image)
        
        # クイックプロンプト
        quick_prompts = [
            "cute cat warrior",
            "magical castle", 
            "dragon in cave",
            "spaceship in space",
            "ninja under cherry tree"
        ]
        
        self.quick_buttons = []
        start_y = y_pos + 60
        for i, prompt in enumerate(quick_prompts):
            btn = SimpleButton(x_margin, start_y + i * 35, input_width, 30, prompt, 
                             lambda p=prompt: self.set_prompt(p))
            self.quick_buttons.append(btn)
    
    def set_width(self, index):
        self.selected_width = index
        
    def set_height(self, index):
        self.selected_height = index
    
    def set_prompt(self, prompt):
        self.prompt_input.text = prompt
    
    def check_server_status(self):
        """サーバーステータスをチェック"""
        def check():
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                data = response.json()
                if data.get('status') == 'healthy' and data.get('pipeline_loaded'):
                    self.server_status = "Connected - Ready to generate"
                else:
                    self.server_status = "Loading AI model..."
            except Exception as e:
                self.server_status = f"Connection error: {str(e)[:40]}"
        
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
        self.generate_button.enabled = False
        self.server_status = "Generating..."
        
        def generate():
            try:
                params = {
                    'prompt': prompt,
                    'negative_prompt': self.negative_prompt_input.text if self.negative_prompt_input.text != self.negative_prompt_input.placeholder else "",
                    'width': self.width_options[self.selected_width],
                    'height': self.height_options[self.selected_height],
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
                        self.server_status = "Generation complete!"
                    else:
                        self.server_status = f"Error: {data.get('error', 'Unknown error')}"
                else:
                    self.server_status = f"HTTP Error: {response.status_code}"
                    
            except Exception as e:
                self.server_status = f"Generation Error: {str(e)[:40]}"
            finally:
                self.generating = False
                self.generate_button.enabled = True
        
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
            
            self.pixel_size_slider.handle_event(event)
            self.palette_size_slider.handle_event(event)
            self.steps_slider.handle_event(event)
            self.guidance_slider.handle_event(event)
            
            self.generate_button.handle_event(event)
            self.save_button.handle_event(event)
            
            for btn in self.width_buttons:
                btn.handle_event(event)
            for btn in self.height_buttons:
                btn.handle_event(event)
            for btn in self.quick_buttons:
                btn.handle_event(event)
        
        # 更新
        self.prompt_input.update(dt)
        self.negative_prompt_input.update(dt)
        self.seed_input.update(dt)
    
    def draw_text(self, surface, text, x, y, font, color):
        """テキストを描画"""
        text_surface, rect = font.render(text, color)
        surface.blit(text_surface, (x, y))
        return rect.height
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill(COLORS['dark_bg'])
        
        # サイドバー
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1])
        pygame.draw.rect(self.screen, COLORS['sidebar_bg'], sidebar_rect)
        
        # タイトル
        self.draw_text(self.screen, "Pixa - AI Pixel Art Generator", 20, 20, 
                      self.title_font, COLORS['text_white'])
        
        # ラベル
        self.draw_text(self.screen, "Prompt", 20, 45, self.label_font, COLORS['text_light'])
        self.draw_text(self.screen, "Negative Prompt", 20, 165, self.label_font, COLORS['text_light'])
        
        # サイズラベル
        self.draw_text(self.screen, "Width", 20, 250, self.label_font, COLORS['text_light'])
        self.draw_text(self.screen, "Height", 210, 250, self.label_font, COLORS['text_light'])
        
        # スライダーラベル
        pixel_val = int(self.pixel_size_slider.val)
        self.draw_text(self.screen, f"Pixel Size: {pixel_val}", 20, 335, self.label_font, COLORS['text_light'])
        
        palette_val = int(self.palette_size_slider.val)
        self.draw_text(self.screen, f"Palette Size: {palette_val}", 20, 395, self.label_font, COLORS['text_light'])
        
        steps_val = int(self.steps_slider.val)
        self.draw_text(self.screen, f"Steps: {steps_val}", 20, 455, self.label_font, COLORS['text_light'])
        
        guidance_val = f"{self.guidance_slider.val:.1f}"
        self.draw_text(self.screen, f"Guidance: {guidance_val}", 20, 515, self.label_font, COLORS['text_light'])
        
        self.draw_text(self.screen, "Seed", 20, 575, self.label_font, COLORS['text_light'])
        
        # メイン表示エリア
        main_rect = pygame.Rect(SIDEBAR_WIDTH, 0, WINDOW_SIZE[0] - SIDEBAR_WIDTH, WINDOW_SIZE[1])
        pygame.draw.rect(self.screen, COLORS['darker_bg'], main_rect)
        
        # 画像表示
        if self.current_image:
            # 画像をメインエリアの中央に配置
            image_rect = self.current_image.get_rect()
            
            # アスペクト比を保持してリサイズ
            max_width = main_rect.width - 40
            max_height = main_rect.height - 40
            
            scale_x = max_width / image_rect.width
            scale_y = max_height / image_rect.height
            scale = min(scale_x, scale_y, 1.0)
            
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
        else:
            # プレースホルダー
            placeholder_text = "Generated image will appear here"
            self.draw_text(self.screen, placeholder_text, 
                          main_rect.centerx - 150, main_rect.centery, 
                          self.font, COLORS['text_gray'])
        
        # UI要素描画
        self.prompt_input.draw(self.screen, self.font)
        self.negative_prompt_input.draw(self.screen, self.font)
        self.seed_input.draw(self.screen, self.font)
        
        self.pixel_size_slider.draw(self.screen, self.font)
        self.palette_size_slider.draw(self.screen, self.font)
        self.steps_slider.draw(self.screen, self.font)
        self.guidance_slider.draw(self.screen, self.font)
        
        # サイズボタン（選択状態を表示）
        for i, btn in enumerate(self.width_buttons):
            if i == self.selected_width:
                pygame.draw.rect(self.screen, COLORS['pixel_primary'], 
                               pygame.Rect(btn.rect.x-2, btn.rect.y-2, btn.rect.width+4, btn.rect.height+4))
            btn.draw(self.screen, self.font)
            
        for i, btn in enumerate(self.height_buttons):
            if i == self.selected_height:
                pygame.draw.rect(self.screen, COLORS['pixel_primary'], 
                               pygame.Rect(btn.rect.x-2, btn.rect.y-2, btn.rect.width+4, btn.rect.height+4))
            btn.draw(self.screen, self.font)
        
        self.generate_button.draw(self.screen, self.font)
        self.save_button.draw(self.screen, self.font)
        
        for btn in self.quick_buttons:
            btn.draw(self.screen, self.label_font)
        
        # ステータス表示
        self.draw_text(self.screen, f"Status: {self.server_status}", 20, WINDOW_SIZE[1] - 25, 
                      self.label_font, COLORS['text_light'])
        
        # 操作説明
        help_text = "Ctrl+Enter: Generate | Ctrl+S: Save"
        self.draw_text(self.screen, help_text, SIDEBAR_WIDTH + 20, WINDOW_SIZE[1] - 25, 
                      self.label_font, COLORS['text_gray'])
        
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