"""
ピクセルアート特化モデルの設定
各モデルのトリガーワード、推奨設定、特徴を管理
"""

MODEL_CONFIGS = {
    # 汎用モデル
    'runwayml/stable-diffusion-v1-5': {
        'name': 'Stable Diffusion v1.5（標準）',
        'trigger_words': [],
        'style_keywords': ['pixel art', '8-bit style', 'retro game', 'sprite'],
        'negative_prompt_additions': ['blurry', 'low quality', 'bad anatomy'],
        'optimal_settings': {
            'pixel_size': 8,
            'palette_size': 16,
            'steps': 20,
            'guidance_scale': 7.5
        }
    },
    
    # PublicPrompts/All-In-One-Pixel-Model
    'PublicPrompts/All-In-One-Pixel-Model': {
        'name': 'All-In-One Pixel Model（推奨）🎮',
        'trigger_words': ['pixelsprite', '16bitscene'],  # キャラ/背景で使い分け
        'style_keywords': [],  # トリガーワードで十分
        'negative_prompt_additions': ['high resolution', 'realistic'],
        'optimal_settings': {
            'pixel_size': 8,
            'palette_size': 16,
            'steps': 25,
            'guidance_scale': 7.5
        }
    },
    
    # スプライトシート生成モデル
    'Onodofthenorth/SD_PixelArt_SpriteSheet_Generator': {
        'name': 'スプライトシート生成（4方向）🕹️',
        'trigger_words': {
            'front': 'PixelartFSS',
            'right': 'PixelartRSS',
            'back': 'PixelartBSS',
            'left': 'PixelartLSS'
        },
        'style_keywords': ['sprite sheet'],
        'negative_prompt_additions': ['blurry', 'high resolution'],
        'optimal_settings': {
            'pixel_size': 16,
            'palette_size': 8,
            'steps': 20,
            'guidance_scale': 7.0,
            'width': 512,
            'height': 512
        }
    },
    
    # シンプルなピクセルアートスタイル
    'kohbanye/pixel-art-style': {
        'name': 'Pixel Art Style（シンプル）🎨',
        'trigger_words': ['pixelartstyle'],
        'style_keywords': ['. in pixel art style'],  # pixel party風のスタイルを追加
        'negative_prompt_additions': ['3d render', 'realistic'],
        'optimal_settings': {
            'pixel_size': 8,
            'palette_size': 16,
            'steps': 20,
            'guidance_scale': 7.5
        },
        'requires_ckpt': True,  # .ckptファイルが必要
        'ckpt_path': './models/pixel-art-style/pixel-art-style.ckpt'
    },
    
    # nerijs/pixel-art-xl (LoRA - SD1.5で使用)
    'nerijs/pixel-art-xl': {
        'name': 'Pixel Art XL LoRA（高速）✨',
        'trigger_words': ['pixel'],
        'style_keywords': ['. in pixel art style'],  # pixel party風のスタイルを追加
        'negative_prompt_additions': ['3d render', 'realistic', 'photo'],
        'optimal_settings': {
            'pixel_size': 6,
            'palette_size': 24,
            'steps': 15,
            'guidance_scale': 7.0
        }
    }
}

def get_model_config(model_id):
    """モデル設定を取得"""
    return MODEL_CONFIGS.get(model_id, MODEL_CONFIGS['runwayml/stable-diffusion-v1-5'])

def enhance_prompt_for_model(prompt, model_id, context=None):
    """
    モデルに応じてプロンプトを最適化
    
    Args:
        prompt: 元のプロンプト
        model_id: 使用するモデルのID
        context: 追加のコンテキスト情報（例：{'direction': 'front'}）
    
    Returns:
        str: 最適化されたプロンプト
    """
    config = get_model_config(model_id)
    enhanced_prompt = prompt
    
    # トリガーワードの追加
    if config['trigger_words']:
        # 辞書形式の場合（方向指定など）
        if isinstance(config['trigger_words'], dict):
            if context and 'direction' in context:
                direction = context['direction']
                if direction in config['trigger_words']:
                    trigger = config['trigger_words'][direction]
                    if trigger.lower() not in enhanced_prompt.lower():
                        enhanced_prompt = f"{trigger}, {enhanced_prompt}"
            else:
                # デフォルトは前向き
                trigger = config['trigger_words'].get('front', '')
                if trigger and trigger.lower() not in enhanced_prompt.lower():
                    enhanced_prompt = f"{trigger}, {enhanced_prompt}"
        
        # リスト形式の場合
        elif isinstance(config['trigger_words'], list):
            # コンテキストに基づいて適切なトリガーを選択
            if context and 'type' in context:
                if context['type'] == 'character' and 'pixelsprite' in config['trigger_words']:
                    enhanced_prompt = f"pixelsprite, {enhanced_prompt}"
                elif context['type'] == 'background' and '16bitscene' in config['trigger_words']:
                    enhanced_prompt = f"16bitscene, {enhanced_prompt}"
            else:
                # デフォルトは最初のトリガーワード
                trigger = config['trigger_words'][0]
                if trigger.lower() not in enhanced_prompt.lower():
                    enhanced_prompt = f"{trigger}, {enhanced_prompt}"
    
    # スタイルキーワードの追加
    prompt_lower = enhanced_prompt.lower()
    for keyword in config['style_keywords']:
        if keyword not in prompt_lower:
            enhanced_prompt = f"{enhanced_prompt}, {keyword}"
    
    return enhanced_prompt

def enhance_negative_prompt_for_model(negative_prompt, model_id):
    """
    モデルに応じてネガティブプロンプトを最適化
    """
    config = get_model_config(model_id)
    enhanced_negative = negative_prompt
    
    # モデル固有のネガティブプロンプトを追加
    negative_lower = enhanced_negative.lower()
    for addition in config['negative_prompt_additions']:
        if addition not in negative_lower:
            enhanced_negative = f"{enhanced_negative}, {addition}"
    
    return enhanced_negative
