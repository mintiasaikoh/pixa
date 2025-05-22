#!/usr/bin/env python3
"""
Pixa - pygame版 AIピクセルアート生成アプリケーション
"""

import pygame
import pygame_gui
import sys
import os
import requests
import json
import threading
import time
from io import BytesIO
import base64
from PIL import Image
import imageio

# 定数
WINDOW_SIZE = (1200, 800)
SIDEBAR_WIDTH = 350
COLORS = {
    'bg': (25, 25, 35),
    'sidebar': (35, 35, 45),
    'button': (65, 105, 225),
    'button_hover': (85, 125, 245),
    'text': (255, 255, 255),
    'panel': (45, 45, 55),
    'accent': (138, 43, 226)
}

class PixaApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Pixa - AI Pixel Art Generator")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager(WINDOW_SIZE, 'data/theme.json')
        
        # 状態管理
        self.current_image = None
        self.generating = False
        self.server_status = "接続中..."
        self.animation_frames = []  # アニメーションフレーム
        self.current_frame = 0  # 現在のフレーム
        self.animation_playing = False  # アニメーション再生中か
        self.last_frame_time = 0  # 最後のフレーム更新時刻
        
        # API設定
        self.api_url = "http://localhost:5001"
        
        self.setup_ui()
        self.check_server_status()
        
    def setup_ui(self):
        """UIコンポーネントを設定"""
        # プロンプト入力
        self.prompt_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(20, 20, SIDEBAR_WIDTH-40, 30),
            manager=self.ui_manager,
            placeholder_text="プロンプトを入力..."
        )
        
        # ネガティブプロンプト
        self.negative_prompt_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(20, 70, SIDEBAR_WIDTH-40, 30),
            manager=self.ui_manager,
            placeholder_text="ネガティブプロンプト"
        )
        
        # サイズ設定
        self.width_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 120, SIDEBAR_WIDTH-100, 20),
            start_value=512,
            value_range=(256, 1024),
            manager=self.ui_manager
        )
        
        self.height_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 160, SIDEBAR_WIDTH-100, 20),
            start_value=512,
            value_range=(256, 1024),
            manager=self.ui_manager
        )
        
        # ピクセルサイズ
        self.pixel_size_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 200, SIDEBAR_WIDTH-100, 20),
            start_value=8,
            value_range=(2, 20),
            manager=self.ui_manager
        )
        
        # パレットサイズ
        self.palette_size_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 240, SIDEBAR_WIDTH-100, 20),
            start_value=16,
            value_range=(4, 64),
            manager=self.ui_manager
        )
        
        # ステップ数
        self.steps_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 280, SIDEBAR_WIDTH-100, 20),
            start_value=20,
            value_range=(10, 50),
            manager=self.ui_manager
        )
        
        # ガイダンススケール
        self.guidance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 320, SIDEBAR_WIDTH-100, 20),
            start_value=7.5,
            value_range=(1.0, 20.0),
            manager=self.ui_manager
        )
        
        # シード
        self.seed_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(20, 360, SIDEBAR_WIDTH-40, 30),
            manager=self.ui_manager,
            placeholder_text="シード（空白でランダム）"
        )
        
        # 生成ボタン
        self.generate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 410, SIDEBAR_WIDTH-40, 50),
            text="ピクセルアートを生成",
            manager=self.ui_manager
        )
        
        # アニメーション設定セパレータ
        self.animation_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 470, SIDEBAR_WIDTH-40, 20),
            text="--- アニメーション設定 ---",
            manager=self.ui_manager
        )
        
        # アニメーションタイプドロップダウン
        self.animation_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['idle', 'walk', 'bounce', 'glow', 'rotate'],
            starting_option='idle',
            relative_rect=pygame.Rect(20, 500, SIDEBAR_WIDTH-40, 30),
            manager=self.ui_manager
        )
        
        # フレーム数スライダー
        self.frame_count_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 540, SIDEBAR_WIDTH-100, 20),
            start_value=4,
            value_range=(2, 16),
            manager=self.ui_manager
        )
        
        # FPSスライダー
        self.fps_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(20, 580, SIDEBAR_WIDTH-100, 20),
            start_value=10,
            value_range=(5, 30),
            manager=self.ui_manager
        )
        
        # アニメーション生成ボタン
        self.generate_animation_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 620, SIDEBAR_WIDTH-40, 40),
            text="アニメーションを生成",
            manager=self.ui_manager
        )
        
        # 保存ボタン
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, 670, (SIDEBAR_WIDTH-50)//2, 40),
            text="保存",
            manager=self.ui_manager
        )
        
        # GIF保存ボタン
        self.save_gif_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SIDEBAR_WIDTH-50)//2 + 30, 670, (SIDEBAR_WIDTH-50)//2, 40),
            text="GIF保存",
            manager=self.ui_manager
        )
        
        # クイックプロンプトボタン
        quick_prompts = [
            "可愛い猫",
            "勇者",
            "ドラゴン",
            "城",
            "宇宙船"
        ]
        
        self.quick_buttons = []
        for i, prompt in enumerate(quick_prompts):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(20, 720 + i * 35, SIDEBAR_WIDTH-40, 30),
                text=prompt,
                manager=self.ui_manager
            )
            self.quick_buttons.append((button, prompt))
        
        # ラベル
        self.labels = []
        label_texts = [
            (110, "幅"), (150, "高さ"), (190, "ピクセルサイズ"),
            (230, "パレット"), (270, "ステップ"), (310, "ガイダンス"),
            (530, "フレーム数"), (570, "FPS")
        ]
        
        for y, text in label_texts:
            self.labels.append((text, y))
    
    def check_server_status(self):
        """サーバーステータスをチェック"""
        def check():
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                data = response.json()
                if data.get('status') == 'healthy' and data.get('pipeline_loaded'):
                    self.server_status = "接続成功"
                else:
                    self.server_status = "モデル読み込み中"
            except Exception as e:
                self.server_status = f"接続エラー: {str(e)}"
        
        threading.Thread(target=check, daemon=True).start()
    
    def generate_image(self):
        """画像生成を実行"""
        if self.generating:
            return
            
        prompt = self.prompt_input.get_text()
        if not prompt.strip():
            return
        
        self.generating = True
        self.generate_button.set_text("生成中...")
        
        def generate():
            try:
                params = {
                    'prompt': prompt,
                    'negative_prompt': self.negative_prompt_input.get_text(),
                    'width': int(self.width_slider.get_current_value()),
                    'height': int(self.height_slider.get_current_value()),
                    'pixel_size': int(self.pixel_size_slider.get_current_value()),
                    'palette_size': int(self.palette_size_slider.get_current_value()),
                    'steps': int(self.steps_slider.get_current_value()),
                    'guidance_scale': self.guidance_slider.get_current_value(),
                    'seed': int(self.seed_input.get_text()) if self.seed_input.get_text().isdigit() else None
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
                        image_string = pil_image.tobytes()
                        pygame_image = pygame.image.fromstring(image_string, pil_image.size, pil_image.mode)
                        
                        self.current_image = pygame_image
                        self.animation_frames = []  # 静止画生成時はアニメーションをリセット
                        self.animation_playing = False
                        self.server_status = "生成完了"
                    else:
                        self.server_status = f"エラー: {data.get('error', '不明なエラー')}"
                else:
                    self.server_status = f"HTTP エラー: {response.status_code}"
                    
            except Exception as e:
                self.server_status = f"生成エラー: {str(e)}"
            finally:
                self.generating = False
                self.generate_button.set_text("ピクセルアートを生成")
        
        threading.Thread(target=generate, daemon=True).start()
    
    def save_image(self):
        """画像を保存"""
        save_image = None
        
        # アニメーション再生中の場合は現在のフレームを保存
        if self.animation_playing and self.animation_frames:
            save_image = self.animation_frames[self.current_frame]
        elif self.current_image:
            save_image = self.current_image
        
        if save_image:
            timestamp = int(time.time())
            filename = f"pixel_art_{timestamp}.png"
            pygame.image.save(save_image, filename)
            self.server_status = f"保存完了: {filename}"
        else:
            self.server_status = "保存する画像がありません"
    
    def generate_animation(self):
        """アニメーション生成を実行"""
        if self.generating:
            return
            
        prompt = self.prompt_input.get_text()
        if not prompt.strip():
            return
        
        self.generating = True
        self.generate_animation_button.set_text("アニメーション生成中...")
        
        def generate():
            try:
                params = {
                    'prompt': prompt,
                    'negative_prompt': self.negative_prompt_input.get_text(),
                    'animation_type': self.animation_type_dropdown.selected_option,
                    'frame_count': int(self.frame_count_slider.get_current_value()),
                    'fps': int(self.fps_slider.get_current_value()),
                    'width': int(self.width_slider.get_current_value()),
                    'height': int(self.height_slider.get_current_value()),
                    'pixel_size': int(self.pixel_size_slider.get_current_value()),
                    'palette_size': int(self.palette_size_slider.get_current_value()),
                    'steps': int(self.steps_slider.get_current_value()),
                    'guidance_scale': self.guidance_slider.get_current_value(),
                    'seed': int(self.seed_input.get_text()) if self.seed_input.get_text().isdigit() else None
                }
                
                response = requests.post(
                    f"{self.api_url}/generate_animation",
                    json=params,
                    timeout=180
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('success'):
                        # Base64 GIFをフレームに分解
                        gif_data = data['image'].split(',')[1]
                        gif_bytes = base64.b64decode(gif_data)
                        
                        # GIFを一時保存してフレームを読み込む
                        temp_gif_path = "temp_animation.gif"
                        with open(temp_gif_path, 'wb') as f:
                            f.write(gif_bytes)
                        
                        # GIFからフレームを読み込む
                        gif_reader = imageio.get_reader(temp_gif_path)
                        self.animation_frames = []
                        
                        for frame in gif_reader:
                            # numpy配列からPIL画像に変換
                            pil_frame = Image.fromarray(frame)
                            # PILからpygameサーフェスに変換
                            frame_string = pil_frame.tobytes()
                            pygame_frame = pygame.image.fromstring(frame_string, pil_frame.size, pil_frame.mode)
                            self.animation_frames.append(pygame_frame)
                        
                        gif_reader.close()
                        os.remove(temp_gif_path)
                        
                        self.current_frame = 0
                        self.animation_playing = True
                        self.last_frame_time = pygame.time.get_ticks()
                        self.server_status = f"アニメーション生成完了: {len(self.animation_frames)}フレーム"
                    else:
                        self.server_status = f"エラー: {data.get('error', '不明なエラー')}"
                else:
                    self.server_status = f"HTTP エラー: {response.status_code}"
                    
            except Exception as e:
                self.server_status = f"アニメーション生成エラー: {str(e)}"
            finally:
                self.generating = False
                self.generate_animation_button.set_text("アニメーションを生成")
        
        threading.Thread(target=generate, daemon=True).start()
    
    def save_gif(self):
        """GIFアニメーションを保存"""
        if self.animation_frames:
            timestamp = int(time.time())
            filename = f"pixel_animation_{timestamp}.gif"
            
            # pygame surfaceをPIL画像に変換
            pil_frames = []
            for frame in self.animation_frames:
                frame_string = pygame.image.tostring(frame, 'RGB')
                size = frame.get_size()
                pil_frame = Image.frombytes('RGB', size, frame_string)
                pil_frames.append(pil_frame)
            
            # GIFとして保存
            fps = int(self.fps_slider.get_current_value())
            duration = 1000 // fps  # ミリ秒単位
            pil_frames[0].save(
                filename,
                save_all=True,
                append_images=pil_frames[1:],
                duration=duration,
                loop=0
            )
            
            self.server_status = f"GIF保存完了: {filename}"
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # UI Events
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.generate_button:
                    self.generate_image()
                elif event.ui_element == self.save_button:
                    self.save_image()
                elif event.ui_element == self.generate_animation_button:
                    self.generate_animation()
                elif event.ui_element == self.save_gif_button:
                    self.save_gif()
                else:
                    # クイックプロンプトボタンチェック
                    for button, prompt in self.quick_buttons:
                        if event.ui_element == button:
                            self.prompt_input.set_text(prompt)
                            break
            
            # キーボードショートカット
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.generate_image()
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_image()
            
            self.ui_manager.process_events(event)
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill(COLORS['bg'])
        
        # サイドバー
        pygame.draw.rect(self.screen, COLORS['sidebar'], (0, 0, SIDEBAR_WIDTH, WINDOW_SIZE[1]))
        
        # メイン表示エリア
        main_rect = pygame.Rect(SIDEBAR_WIDTH, 0, WINDOW_SIZE[0] - SIDEBAR_WIDTH, WINDOW_SIZE[1])
        pygame.draw.rect(self.screen, COLORS['panel'], main_rect)
        
        # 画像表示
        display_image = None
        
        # アニメーション再生中の場合
        if self.animation_playing and self.animation_frames:
            # フレームの更新タイミングをチェック
            current_time = pygame.time.get_ticks()
            fps = int(self.fps_slider.get_current_value())
            frame_duration = 1000 // fps
            
            if current_time - self.last_frame_time >= frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.last_frame_time = current_time
            
            display_image = self.animation_frames[self.current_frame]
        elif self.current_image:
            display_image = self.current_image
        
        if display_image:
            # 画像をメインエリアの中央に配置
            image_rect = display_image.get_rect()
            
            # アスペクト比を保持してリサイズ
            max_width = main_rect.width - 40
            max_height = main_rect.height - 40
            
            scale_x = max_width / image_rect.width
            scale_y = max_height / image_rect.height
            scale = min(scale_x, scale_y, 1.0)  # 1.0を超えない
            
            if scale < 1.0:
                new_width = int(image_rect.width * scale)
                new_height = int(image_rect.height * scale)
                scaled_image = pygame.transform.scale(display_image, (new_width, new_height))
            else:
                scaled_image = display_image
                new_width, new_height = image_rect.size
            
            # 中央配置
            x = SIDEBAR_WIDTH + (main_rect.width - new_width) // 2
            y = (main_rect.height - new_height) // 2
            
            self.screen.blit(scaled_image, (x, y))
        else:
            # プレースホルダー
            font = pygame.font.Font(None, 36)
            text = font.render("生成された画像がここに表示されます", True, COLORS['text'])
            text_rect = text.get_rect(center=main_rect.center)
            self.screen.blit(text, text_rect)
        
        # ラベル描画
        font = pygame.font.Font(None, 24)
        for text, y in self.labels:
            label = font.render(text, True, COLORS['text'])
            self.screen.blit(label, (SIDEBAR_WIDTH - 80, y))
        
        # ステータス表示
        status_font = pygame.font.Font(None, 20)
        status_text = status_font.render(f"Status: {self.server_status}", True, COLORS['text'])
        self.screen.blit(status_text, (10, WINDOW_SIZE[1] - 25))
        
        # スライダー値表示
        value_font = pygame.font.Font(None, 18)
        slider_values = [
            (f"{int(self.width_slider.get_current_value())}", 130),
            (f"{int(self.height_slider.get_current_value())}", 170),
            (f"{int(self.pixel_size_slider.get_current_value())}", 210),
            (f"{int(self.palette_size_slider.get_current_value())}", 250),
            (f"{int(self.steps_slider.get_current_value())}", 290),
            (f"{self.guidance_slider.get_current_value():.1f}", 330),
            (f"{int(self.frame_count_slider.get_current_value())}", 550),
            (f"{int(self.fps_slider.get_current_value())}", 590)
        ]
        
        for value, y in slider_values:
            value_text = value_font.render(value, True, COLORS['text'])
            self.screen.blit(value_text, (SIDEBAR_WIDTH - 40, y))
        
        # UI描画
        self.ui_manager.draw_ui(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """メインループ"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.ui_manager.update(time_delta)
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    """エントリーポイント"""
    # データディレクトリ作成
    os.makedirs('data', exist_ok=True)
    
    # テーマファイル作成
    theme_data = {
        "button": {
            "colours": {
                "normal_bg": "#4169E1",
                "hovered_bg": "#557BF5",
                "disabled_bg": "#666666",
                "selected_bg": "#8A2BE2",
                "normal_text": "#FFFFFF",
                "hovered_text": "#FFFFFF",
                "selected_text": "#FFFFFF",
                "disabled_text": "#888888"
            }
        },
        "text_entry_line": {
            "colours": {
                "normal_bg": "#2D2D35",
                "focused_bg": "#35353D",
                "normal_border": "#666666",
                "focused_border": "#4169E1"
            }
        },
        "horizontal_slider": {
            "colours": {
                "normal_bg": "#2D2D35",
                "hovered_bg": "#35353D",
                "selected_bg": "#4169E1"
            }
        }
    }
    
    with open('data/theme.json', 'w') as f:
        json.dump(theme_data, f, indent=2)
    
    app = PixaApp()
    app.run()

if __name__ == "__main__":
    main()