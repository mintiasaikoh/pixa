#!/usr/bin/env python3
"""
Pixa - pygame版 AIピクセルアート生成アプリケーション (改良版)
日本語入力対応 + 美しいUI
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
WINDOW_SIZE = (1600, 1000)
SIDEBAR_WIDTH = 450
COLORS = {
    'bg': (15, 15, 25),
    'sidebar': (25, 25, 35),
    'card': (35, 35, 45),
    'button': (70, 130, 250),
    'button_hover': (90, 150, 255),
    'button_active': (50, 110, 230),
    'success': (40, 200, 100),
    'error': (250, 80, 80),
    'warning': (255, 180, 0),
    'text': (255, 255, 255),
    'text_secondary': (180, 180, 190),
    'text_dim': (120, 120, 130),
    'input_bg': (45, 45, 55),
    'input_border': (80, 80, 90),
    'input_focus': (70, 130, 250),
    'slider_bg': (60, 60, 70),
    'slider_track': (100, 100, 110),
    'slider_handle': (70, 130, 250),
    'quick_button': (60, 60, 75),
    'quick_button_hover': (80, 80, 95)
}

class ModernButton:
    def __init__(self, x, y, width, height, text, callback=None, style='primary'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.style = style
        self.hovered = False
        self.pressed = False
        self.disabled = False
        
    def handle_event(self, event):
        if self.disabled:
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
        if self.disabled:
            color = COLORS['text_dim']
        elif self.pressed:
            color = COLORS['button_active']
        elif self.hovered:
            color = COLORS['button_hover']
        else:
            color = COLORS['button']
            
        # 影効果
        shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=8)
        
        # ボタン本体
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # テキスト
        text_color = COLORS['text'] if not self.disabled else COLORS['text_dim']
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class ModernSlider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label="", suffix=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.suffix = suffix
        self.dragging = False
        self.hovered = False
        
    def handle_event(self, event):
        handle_pos = self.get_handle_pos()
        handle_rect = pygame.Rect(handle_pos - 12, self.rect.y - 6, 24, self.rect.height + 12)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos)
            if self.dragging:
                self.update_value(event.pos[0])
    
    def get_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + ratio * self.rect.width
    
    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        rel_x = max(0, min(rel_x, self.rect.width))
        ratio = rel_x / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        
    def draw(self, screen, font, label_font):
        # ラベル
        if self.label:
            if isinstance(self.val, float):
                value_text = f"{self.val:.1f}{self.suffix}"
            else:
                value_text = f"{int(self.val)}{self.suffix}"
            
            label_text = f"{self.label}: {value_text}"
            label_surface = label_font.render(label_text, True, COLORS['text'])
            screen.blit(label_surface, (self.rect.x, self.rect.y - 30))
        
        # スライダーバー背景
        pygame.draw.rect(screen, COLORS['slider_bg'], self.rect, border_radius=6)
        
        # 進行バー
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        progress_width = ratio * self.rect.width
        progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
        pygame.draw.rect(screen, COLORS['slider_handle'], progress_rect, border_radius=6)
        
        # ハンドル
        handle_pos = self.get_handle_pos()
        handle_color = COLORS['button_hover'] if self.hovered else COLORS['slider_handle']
        pygame.draw.circle(screen, handle_color, (int(handle_pos), self.rect.centery), 12)
        pygame.draw.circle(screen, COLORS['text'], (int(handle_pos), self.rect.centery), 8)

class ModernTextInput:
    def __init__(self, x, y, width, height, placeholder="", multiline=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.multiline = multiline
        self.scroll_y = 0
        self.lines = [""]
        self.cursor_line = 0
        self.cursor_pos = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_pos-1] + line[self.cursor_pos:]
                    self.cursor_pos -= 1
                elif self.cursor_line > 0 and self.multiline:
                    # 前の行と結合
                    prev_line = self.lines[self.cursor_line - 1]
                    current_line = self.lines[self.cursor_line]
                    self.cursor_pos = len(prev_line)
                    self.lines[self.cursor_line - 1] = prev_line + current_line
                    del self.lines[self.cursor_line]
                    self.cursor_line -= 1
                self.update_text()
                    
            elif event.key == pygame.K_RETURN:
                if self.multiline:
                    line = self.lines[self.cursor_line]
                    left_part = line[:self.cursor_pos]
                    right_part = line[self.cursor_pos:]
                    self.lines[self.cursor_line] = left_part
                    self.lines.insert(self.cursor_line + 1, right_part)
                    self.cursor_line += 1
                    self.cursor_pos = 0
                    self.update_text()
                    
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                elif self.cursor_line > 0 and self.multiline:
                    self.cursor_line -= 1
                    self.cursor_pos = len(self.lines[self.cursor_line])
                    
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.lines[self.cursor_line]):
                    self.cursor_pos += 1
                elif self.cursor_line < len(self.lines) - 1 and self.multiline:
                    self.cursor_line += 1
                    self.cursor_pos = 0
                    
            elif event.key == pygame.K_UP and self.multiline:
                if self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_pos = min(self.cursor_pos, len(self.lines[self.cursor_line]))
                    
            elif event.key == pygame.K_DOWN and self.multiline:
                if self.cursor_line < len(self.lines) - 1:
                    self.cursor_line += 1
                    self.cursor_pos = min(self.cursor_pos, len(self.lines[self.cursor_line]))
                    
            elif event.unicode and event.unicode.isprintable():
                # 日本語を含む全ての文字に対応
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_pos] + event.unicode + line[self.cursor_pos:]
                self.cursor_pos += 1
                self.update_text()
    
    def update_text(self):
        self.text = '\n'.join(self.lines) if self.multiline else self.lines[0]
        
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen, font):
        # 背景とボーダー
        border_color = COLORS['input_focus'] if self.active else COLORS['input_border']
        pygame.draw.rect(screen, COLORS['input_bg'], self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # テキスト表示エリア
        text_rect = pygame.Rect(self.rect.x + 15, self.rect.y + 10, 
                               self.rect.width - 30, self.rect.height - 20)
        
        if self.text:
            if self.multiline:
                y_offset = 0
                for i, line in enumerate(self.lines):
                    if y_offset + font.get_height() > text_rect.height:
                        break
                    text_surface = font.render(line, True, COLORS['text'])
                    screen.blit(text_surface, (text_rect.x, text_rect.y + y_offset))
                    
                    # カーソル描画
                    if self.active and self.cursor_visible and i == self.cursor_line:
                        cursor_text = line[:self.cursor_pos]
                        cursor_x = text_rect.x + font.size(cursor_text)[0]
                        pygame.draw.line(screen, COLORS['text'], 
                                       (cursor_x, text_rect.y + y_offset), 
                                       (cursor_x, text_rect.y + y_offset + font.get_height()), 2)
                    y_offset += font.get_height() + 5
            else:
                text_surface = font.render(self.text, True, COLORS['text'])
                screen.blit(text_surface, (text_rect.x, text_rect.centery - text_surface.get_height() // 2))
                
                # カーソル描画
                if self.active and self.cursor_visible:
                    cursor_text = self.text[:self.cursor_pos]
                    cursor_x = text_rect.x + font.size(cursor_text)[0]
                    pygame.draw.line(screen, COLORS['text'], 
                                   (cursor_x, text_rect.y + 5), 
                                   (cursor_x, text_rect.bottom - 5), 2)
        else:
            # プレースホルダー
            placeholder_surface = font.render(self.placeholder, True, COLORS['text_dim'])
            screen.blit(placeholder_surface, (text_rect.x, text_rect.centery - placeholder_surface.get_height() // 2))

class PixaApp:
    def __init__(self):
        pygame.init()
        
        # 日本語入力を有効化
        pygame.key.set_repeat(500, 50)
        
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Pixa - AI Pixel Art Generator")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # フォント設定（日本語対応）
        self.setup_fonts()
        
        # 状態管理
        self.current_image = None
        self.generating = False
        self.server_status = "接続中..."
        self.status_color = COLORS['text_dim']
        
        # API設定
        self.api_url = "http://localhost:5001"
        
        self.setup_ui()
        self.check_server_status()
        
    def setup_fonts(self):
        """日本語対応フォントを設定"""
        font_candidates = [
            'hiraginosans-w3',
            'hiragino sans',
            'noto sans cjk jp',
            'arial unicode ms',
            'yugothic',
            'meiryo'
        ]
        
        self.font = None
        for font_name in font_candidates:
            try:
                self.font = pygame.font.SysFont(font_name, 20)
                self.title_font = pygame.font.SysFont(font_name, 32)
                self.subtitle_font = pygame.font.SysFont(font_name, 16)
                self.label_font = pygame.font.SysFont(font_name, 14)
                break
            except:
                continue
                
        if not self.font:
            # フォールバック
            self.font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 32)
            self.subtitle_font = pygame.font.Font(None, 16)
            self.label_font = pygame.font.Font(None, 14)
    
    def setup_ui(self):
        """美しいUIを設定"""
        margin = 30
        y = 80
        
        # プロンプト入力（大きめ、複数行対応）
        self.prompt_input = ModernTextInput(
            margin, y, SIDEBAR_WIDTH - margin * 2, 100, 
            "プロンプトを入力してください... (日本語OK)", multiline=True
        )
        y += 130
        
        # ネガティブプロンプト
        self.negative_prompt_input = ModernTextInput(
            margin, y, SIDEBAR_WIDTH - margin * 2, 50, 
            "ネガティブプロンプト (optional)"
        )
        y += 80
        
        # パラメータセクション
        y += 20
        
        # 画像サイズ
        self.width_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                       256, 1024, 512, "幅", "px")
        y += 60
        
        self.height_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                        256, 1024, 512, "高さ", "px")
        y += 60
        
        # ピクセルアート設定
        self.pixel_size_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                            2, 20, 8, "ピクセルサイズ", "px")
        y += 60
        
        self.palette_size_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                              4, 64, 16, "カラーパレット", "色")
        y += 60
        
        # 生成設定
        self.steps_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                       10, 50, 20, "生成ステップ数", "")
        y += 60
        
        self.guidance_slider = ModernSlider(margin, y, SIDEBAR_WIDTH - margin * 2, 12, 
                                          1.0, 20.0, 7.5, "ガイダンス強度", "")
        y += 80
        
        # シード入力
        self.seed_input = ModernTextInput(margin, y, SIDEBAR_WIDTH - margin * 2, 50, 
                                        "シード値 (空白でランダム)")
        y += 80
        
        # 生成ボタン
        self.generate_button = ModernButton(margin, y, SIDEBAR_WIDTH - margin * 2, 60, 
                                          "🎨 ピクセルアートを生成", self.generate_image)
        y += 80
        
        # 保存・コピーボタン
        button_width = (SIDEBAR_WIDTH - margin * 3) // 2
        self.save_button = ModernButton(margin, y, button_width, 45, 
                                      "💾 保存", self.save_image)
        self.copy_button = ModernButton(margin * 2 + button_width, y, button_width, 45, 
                                      "📋 コピー", self.copy_image)
        y += 65
        
        # クイックプロンプト
        quick_prompts = [
            "🐱 可愛い猫の戦士",
            "🏰 魔法の城",
            "🐉 かっこいいドラゴン", 
            "🚀 レトロな宇宙船",
            "🌸 桜の木の下の忍者"
        ]
        
        self.quick_buttons = []
        for i, prompt in enumerate(quick_prompts):
            button = ModernButton(margin, y + i * 50, SIDEBAR_WIDTH - margin * 2, 40, 
                                prompt, lambda p=prompt.split(' ', 1)[1]: self.set_prompt(p))
            self.quick_buttons.append(button)
    
    def set_prompt(self, prompt):
        """クイックプロンプトを設定"""
        self.prompt_input.text = prompt
        self.prompt_input.lines = [prompt]
        self.prompt_input.cursor_line = 0
        self.prompt_input.cursor_pos = len(prompt)
    
    def check_server_status(self):
        """サーバーステータスをチェック"""
        def check():
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                data = response.json()
                if data.get('status') == 'healthy' and data.get('pipeline_loaded'):
                    self.server_status = "✅ サーバー接続成功"
                    self.status_color = COLORS['success']
                else:
                    self.server_status = "⏳ AIモデル読み込み中..."
                    self.status_color = COLORS['warning']
            except Exception as e:
                self.server_status = f"❌ 接続エラー: {str(e)[:30]}"
                self.status_color = COLORS['error']
        
        threading.Thread(target=check, daemon=True).start()
    
    def generate_image(self):
        """画像生成を実行"""
        if self.generating:
            return
            
        prompt = self.prompt_input.text.strip()
        if not prompt or prompt == self.prompt_input.placeholder:
            self.server_status = "❗ プロンプトを入力してください"
            self.status_color = COLORS['error']
            return
        
        self.generating = True
        self.generate_button.disabled = True
        self.server_status = "🎨 生成中..."
        self.status_color = COLORS['warning']
        
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
                        self.server_status = "✨ 生成完了！"
                        self.status_color = COLORS['success']
                    else:
                        self.server_status = f"❌ エラー: {data.get('error', '不明なエラー')}"
                        self.status_color = COLORS['error']
                else:
                    self.server_status = f"❌ HTTP エラー: {response.status_code}"
                    self.status_color = COLORS['error']
                    
            except Exception as e:
                self.server_status = f"❌ 生成エラー: {str(e)[:30]}"
                self.status_color = COLORS['error']
            finally:
                self.generating = False
                self.generate_button.disabled = False
        
        threading.Thread(target=generate, daemon=True).start()
    
    def save_image(self):
        """画像を保存"""
        if self.current_image:
            timestamp = int(time.time())
            filename = f"pixel_art_{timestamp}.png"
            pygame.image.save(self.current_image, filename)
            self.server_status = f"💾 保存完了: {filename}"
            self.status_color = COLORS['success']
        else:
            self.server_status = "❗ 保存する画像がありません"
            self.status_color = COLORS['error']
    
    def copy_image(self):
        """画像をクリップボードにコピー（macOS用）"""
        if self.current_image:
            try:
                # 一時ファイルに保存してクリップボードにコピー
                temp_filename = "/tmp/pixa_temp.png"
                pygame.image.save(self.current_image, temp_filename)
                
                # macOSのpbcopyを使用
                import subprocess
                subprocess.run(['osascript', '-e', f'set the clipboard to (read file POSIX file "{temp_filename}" as JPEG picture)'])
                
                self.server_status = "📋 クリップボードにコピーしました"
                self.status_color = COLORS['success']
                
                # 一時ファイル削除
                os.remove(temp_filename)
            except Exception as e:
                self.server_status = f"❌ コピーエラー: {str(e)[:30]}"
                self.status_color = COLORS['error']
        else:
            self.server_status = "❗ コピーする画像がありません"
            self.status_color = COLORS['error']
    
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
                elif event.key == pygame.K_c and keys[pygame.K_LCTRL] and not self.prompt_input.active:
                    self.copy_image()
            
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
            self.copy_button.handle_event(event)
            
            for button in self.quick_buttons:
                button.handle_event(event)
        
        # 更新
        self.prompt_input.update(dt)
        self.negative_prompt_input.update(dt)
        self.seed_input.update(dt)
    
    def draw_card(self, surface, rect, title=None):
        """カード風の背景を描画"""
        # 影
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(surface, (0, 0, 0, 30), shadow_rect, border_radius=12)
        
        # カード本体
        pygame.draw.rect(surface, COLORS['card'], rect, border_radius=12)
        
        if title:
            title_surface = self.subtitle_font.render(title, True, COLORS['text_secondary'])
            surface.blit(title_surface, (rect.x + 20, rect.y + 15))
    
    def draw(self):
        """描画処理"""
        # 背景グラデーション風
        for y in range(WINDOW_SIZE[1]):
            color_ratio = y / WINDOW_SIZE[1]
            r = int(15 + color_ratio * 5)
            g = int(15 + color_ratio * 5)
            b = int(25 + color_ratio * 10)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_SIZE[0], y))
        
        # サイドバー
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1])
        self.draw_card(self.screen, sidebar_rect)
        
        # タイトル
        title_text = self.title_font.render("🎨 Pixa", True, COLORS['button'])
        subtitle_text = self.subtitle_font.render("AI ピクセルアート ジェネレーター", True, COLORS['text_secondary'])
        self.screen.blit(title_text, (30, 20))
        self.screen.blit(subtitle_text, (30, 55))
        
        # メイン表示エリア
        main_rect = pygame.Rect(SIDEBAR_WIDTH + 20, 20, 
                               WINDOW_SIZE[0] - SIDEBAR_WIDTH - 40, WINDOW_SIZE[1] - 40)
        self.draw_card(self.screen, main_rect, "生成結果")
        
        # 画像表示
        display_rect = pygame.Rect(main_rect.x + 20, main_rect.y + 50, 
                                 main_rect.width - 40, main_rect.height - 100)
        
        if self.current_image:
            # 画像をメインエリアの中央に配置
            image_rect = self.current_image.get_rect()
            
            # アスペクト比を保持してリサイズ
            scale_x = display_rect.width / image_rect.width
            scale_y = display_rect.height / image_rect.height
            scale = min(scale_x, scale_y, 1.0)
            
            if scale < 1.0:
                new_width = int(image_rect.width * scale)
                new_height = int(image_rect.height * scale)
                scaled_image = pygame.transform.scale(self.current_image, (new_width, new_height))
            else:
                scaled_image = self.current_image
                new_width, new_height = image_rect.size
            
            # 中央配置
            x = display_rect.centerx - new_width // 2
            y = display_rect.centery - new_height // 2
            
            # 画像の影
            shadow_rect = pygame.Rect(x + 4, y + 4, new_width, new_height)
            pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=8)
            
            self.screen.blit(scaled_image, (x, y))
            
            # 画像情報
            info_text = f"📐 {image_rect.width} × {image_rect.height}px"
            info_surface = self.label_font.render(info_text, True, COLORS['text_dim'])
            self.screen.blit(info_surface, (x, y + new_height + 10))
        else:
            # プレースホルダー
            placeholder_text = self.font.render("🖼️ 生成された画像がここに表示されます", True, COLORS['text_dim'])
            text_rect = placeholder_text.get_rect(center=display_rect.center)
            self.screen.blit(placeholder_text, text_rect)
        
        # UI要素描画
        self.prompt_input.draw(self.screen, self.font)
        self.negative_prompt_input.draw(self.screen, self.font)
        self.seed_input.draw(self.screen, self.font)
        
        self.width_slider.draw(self.screen, self.font, self.label_font)
        self.height_slider.draw(self.screen, self.font, self.label_font)
        self.pixel_size_slider.draw(self.screen, self.font, self.label_font)
        self.palette_size_slider.draw(self.screen, self.font, self.label_font)
        self.steps_slider.draw(self.screen, self.font, self.label_font)
        self.guidance_slider.draw(self.screen, self.font, self.label_font)
        
        self.generate_button.draw(self.screen, self.font)
        self.save_button.draw(self.screen, self.subtitle_font)
        self.copy_button.draw(self.screen, self.subtitle_font)
        
        for button in self.quick_buttons:
            button.draw(self.screen, self.subtitle_font)
        
        # ステータス表示
        status_surface = self.font.render(self.server_status, True, self.status_color)
        self.screen.blit(status_surface, (30, WINDOW_SIZE[1] - 40))
        
        # 操作説明
        help_text = "💡 Ctrl+Enter: 生成 | Ctrl+S: 保存 | Ctrl+C: コピー"
        help_surface = self.label_font.render(help_text, True, COLORS['text_dim'])
        self.screen.blit(help_surface, (main_rect.x + 20, WINDOW_SIZE[1] - 25))
        
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