# Pixa用の高度な日本語処理モジュール

import re
import logging

logger = logging.getLogger(__name__)

class PixaJapaneseProcessor:
    """
    Pixaのための高度な日本語処理
    - 複合語の理解
    - 文脈を考慮した翻訳
    - ピクセルアート特化の表現変換
    """
    
    def __init__(self):
        # 複合語・フレーズ辞書（順序重要：長いものから処理）
        self.phrase_dict = {
            # テクノロジー関連の複合語
            'ゲーミングパソコン': 'gaming PC with RGB lighting',
            'ノートパソコンで作業': 'working on laptop computer',
            'パソコンの画面': 'computer monitor screen',
            'キーボードとマウス': 'keyboard and mouse setup',
            'デスクトップパソコン': 'desktop computer setup',
            'レトロなパソコン': 'retro computer, old CRT monitor',
            
            # 状況・シーン
            'パソコンで仕事をする': 'person working at computer',
            'ゲームをプレイする': 'playing video game',
            'コーヒーを飲みながら': 'drinking coffee while',
            '夜遅くまで': 'late at night',
            '朝早く': 'early morning',
            
            # ピクセルアート特有の表現
            'ドット絵風の': 'pixel art style',
            'レトロゲーム風': 'retro game style, 8-bit',
            'ファミコン風': 'NES style, 8-bit',
            'スーファミ風': 'SNES style, 16-bit',
            'ゲームボーイ風': 'gameboy style, green monochrome',
            
            # 場所・環境
            'オフィスで': 'in office',
            '自宅で': 'at home',
            'カフェで': 'in cafe',
            '学校で': 'at school',
            '部屋の中で': 'inside room',
            
            # 感情・雰囲気
            '楽しそうに': 'happily, joyfully',
            '真剣に': 'seriously, focused',
            '疲れた様子で': 'looking tired',
            'リラックスして': 'relaxed',
            '集中して': 'concentrated, focused',
        }
        
        # 文脈を考慮した単語変換
        self.context_aware_dict = {
            'パソコン': {
                'default': 'computer, PC',
                'with_作業': 'computer workstation',
                'with_ゲーム': 'gaming computer',
                'with_古い': 'old retro computer',
                'with_新しい': 'modern computer',
            },
            'キャラクター': {
                'default': 'character',
                'with_ゲーム': 'game character sprite',
                'with_アニメ': 'anime style character',
                'with_かわいい': 'cute chibi character',
            }
        }
        
        # ピクセルアート強化キーワード
        self.pixel_art_enhancers = [
            'pixel art',
            'pixelated',
            'retro game sprite',
            '8-bit style',
            'low resolution',
            'crisp pixels',
            'game asset'
        ]
    
    def process_prompt(self, text):
        """メインの処理関数"""
        # 日本語が含まれているかチェック
        if not self._contains_japanese(text):
            return self._enhance_pixel_art(text)
        
        logger.info(f"Processing Japanese prompt: {text}")
        
        # 1. フレーズ・複合語の処理
        processed = self._process_phrases(text)
        
        # 2. 文脈を考慮した単語処理
        processed = self._process_context_aware(processed)
        
        # 3. 残りの単語を基本辞書で処理
        processed = self._process_basic_words(processed)
        
        # 4. 助詞の処理と整形
        processed = self._clean_and_format(processed)
        
        # 5. ピクセルアート用キーワードの追加
        processed = self._enhance_pixel_art(processed)
        
        logger.info(f"Processed result: {processed}")
        return processed
    
    def _contains_japanese(self, text):
        """日本語が含まれているかチェック"""
        return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    
    def _process_phrases(self, text):
        """フレーズ・複合語の処理"""
        result = text
        for jp_phrase, en_phrase in sorted(self.phrase_dict.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(jp_phrase, en_phrase)
        return result
    
    def _process_context_aware(self, text):
        """文脈を考慮した単語処理"""
        result = text
        for word, contexts in self.context_aware_dict.items():
            if word in result:
                # 文脈を確認
                replacement = contexts['default']
                for context_key, context_value in contexts.items():
                    if context_key.startswith('with_'):
                        trigger = context_key.replace('with_', '')
                        if trigger in result:
                            replacement = context_value
                            break
                result = result.replace(word, replacement)
        return result
    
    def _process_basic_words(self, text):
        """基本的な単語辞書での処理（既存の辞書を使用）"""
        # ここでは既存のtranslate_japanese_to_english関数の辞書を使用
        # 実際の実装では、その辞書をインポートして使用
        return text
    
    def _clean_and_format(self, text):
        """助詞の処理と整形"""
        # 基本的な助詞や接続詞を処理
        text = re.sub(r'[のがをにはでと、。]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _enhance_pixel_art(self, text):
        """ピクセルアート用のキーワード追加"""
        # 既にピクセルアート関連のキーワードが含まれているかチェック
        pixel_keywords = ['pixel', '8-bit', '16-bit', 'retro', 'sprite']
        has_pixel_keyword = any(keyword in text.lower() for keyword in pixel_keywords)
        
        if not has_pixel_keyword:
            # ランダムに1-2個のキーワードを追加
            import random
            num_keywords = random.randint(1, 2)
            selected_keywords = random.sample(self.pixel_art_enhancers[:4], num_keywords)
            text = f"{text}, {', '.join(selected_keywords)}"
        
        return text
    
    def get_negative_prompt_suggestions(self, prompt):
        """プロンプトに基づいたネガティブプロンプトの提案"""
        suggestions = [
            "blurry",
            "low quality",
            "bad anatomy",
            "realistic photo",
            "smooth gradient"
        ]
        
        # パソコン関連の場合
        if any(word in prompt for word in ['computer', 'PC', 'laptop']):
            suggestions.extend([
                "modern UI",
                "photorealistic",
                "high resolution screen"
            ])
        
        # キャラクター関連の場合
        if any(word in prompt for word in ['character', 'person', 'hero']):
            suggestions.extend([
                "bad hands",
                "extra fingers",
                "distorted face"
            ])
        
        return ", ".join(suggestions)

# グローバルインスタンス
pixa_processor = PixaJapaneseProcessor()

def enhanced_translate_japanese_to_english(text):
    """既存の関数を置き換える新しい翻訳関数"""
    return pixa_processor.process_prompt(text)

def get_negative_prompt_suggestions(prompt):
    """ネガティブプロンプトの提案"""
    return pixa_processor.get_negative_prompt_suggestions(prompt)
