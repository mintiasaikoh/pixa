/**
 * Pixa - AI ピクセルアート ジェネレーター
 * 改善版フロントエンドJavaScript
 */

class PixelArtGeneratorImproved {
    constructor() {
        this.apiUrl = '';
        this.isGenerating = false;
        this.currentImage = null;
        this.startTime = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadModels();
        this.checkServerStatus();
    }
    
    initializeElements() {
        // DOM要素の参照を保存
        this.elements = {
            // プロンプト関連
            prompt: document.getElementById('prompt'),
            negativePrompt: document.getElementById('negative-prompt'),
            
            // モデル関連
            model: document.getElementById('model'),
            modelDescription: document.getElementById('model-description'),
            
            // スタイルプリセット
            stylePresets: document.querySelectorAll('.style-preset'),
            
            // パラメータ
            pixelSize: document.getElementById('pixel-size'),
            pixelSizeValue: document.getElementById('pixel-size-value'),
            paletteSize: document.getElementById('palette-size'),
            paletteSizeValue: document.getElementById('palette-size-value'),
            steps: document.getElementById('steps'),
            stepsValue: document.getElementById('steps-value'),
            imageSize: document.getElementById('image-size'),
            
            // ボタン
            generateBtn: document.getElementById('generate-btn'),
            generateSpriteBtn: document.getElementById('generate-sprite-btn'),
            generateGlitchBtn: document.getElementById('generate-glitch-btn'),
            downloadBtn: document.getElementById('download-btn'),
            copyBtn: document.getElementById('copy-btn'),
            shareBtn: document.getElementById('share-btn'),
            animateBtn: document.getElementById('animate-btn'),
            
            // 表示エリア
            placeholder: document.getElementById('placeholder'),
            progress: document.getElementById('progress'),
            progressMessage: document.getElementById('progress-message'),
            progressTime: document.getElementById('progress-time'),
            result: document.getElementById('result'),
            resultImage: document.getElementById('result-image'),
            imageControls: document.getElementById('image-controls'),
            
            // トースト
            toast: document.getElementById('toast'),
            toastMessage: document.getElementById('toast-message'),
            
            // グリッチアート設定
            glitchModal: new bootstrap.Modal(document.getElementById('glitchModal')),
            glitchStyle: document.getElementById('glitch-style'),
            glitchPixelSize: document.getElementById('glitch-pixel-size'),
            glitchPixelSizeValue: document.getElementById('glitch-pixel-size-value'),
            glitchAnimation: document.getElementById('glitch-animation'),
            generateGlitchConfirm: document.getElementById('generate-glitch-confirm')
        };
    }
    
    bindEvents() {
        // 生成ボタン
        this.elements.generateBtn.addEventListener('click', () => this.generateImage());
        
        // 特殊生成ボタン
        this.elements.generateSpriteBtn?.addEventListener('click', () => this.generateSpriteSheet());
        this.elements.generateGlitchBtn?.addEventListener('click', () => this.showGlitchModal());
        
        // Ctrl+Enterで生成
        this.elements.prompt.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                this.generateImage();
            }
        });
        
        // レンジスライダー
        const sliders = ['pixelSize', 'paletteSize', 'steps'];
        sliders.forEach(name => {
            const slider = this.elements[name];
            const value = this.elements[name + 'Value'];
            
            slider?.addEventListener('input', (e) => {
                const suffix = name === 'paletteSize' ? '色' : '';
                value.textContent = e.target.value + suffix;
            });
        });
        
        // グリッチアートのピクセルサイズ
        this.elements.glitchPixelSize?.addEventListener('input', (e) => {
            this.elements.glitchPixelSizeValue.textContent = e.target.value;
        });
        
        // スタイルプリセット
        this.elements.stylePresets.forEach(preset => {
            preset.addEventListener('click', () => this.applyPreset(preset));
        });
        
        // モデル選択
        this.elements.model?.addEventListener('change', () => this.updateModelDescription());
        
        // イメージコントロール
        this.elements.downloadBtn?.addEventListener('click', () => this.downloadImage());
        this.elements.copyBtn?.addEventListener('click', () => this.copyImage());
        this.elements.shareBtn?.addEventListener('click', () => this.shareImage());
        this.elements.animateBtn?.addEventListener('click', () => this.animateImage());
        
        // グリッチアート生成確認
        this.elements.generateGlitchConfirm?.addEventListener('click', () => this.generateGlitchArt());
    }
    
    async loadModels() {
        try {
            const response = await fetch('/models');
            const data = await response.json();
            
            if (data.success && data.models) {
                // モデル選択を更新
                this.elements.model.innerHTML = '';
                
                Object.entries(data.configs).forEach(([id, config]) => {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = config.name;
                    this.elements.model.appendChild(option);
                });
                
                this.updateModelDescription();
            }
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }
    
    updateModelDescription() {
        const descriptions = {
            'PublicPrompts/All-In-One-Pixel-Model': '最も汎用性の高いピクセルアートモデル',
            'runwayml/stable-diffusion-v1-5': '標準的な画像生成モデル',
            'Onodofthenorth/SD_PixelArt_SpriteSheet_Generator': 'ゲーム開発向け4方向スプライト',
            'nerijs/pixel-art-xl': '高速生成に最適化されたLoRAモデル'
        };
        
        const modelId = this.elements.model.value;
        this.elements.modelDescription.textContent = descriptions[modelId] || '';
    }
    
    applyPreset(presetElement) {
        // アクティブ状態を更新
        this.elements.stylePresets.forEach(p => p.classList.remove('active'));
        presetElement.classList.add('active');
        
        const presetName = presetElement.dataset.preset;
        const presets = {
            '8bit': { pixelSize: 8, paletteSize: 16, steps: 20 },
            '16bit': { pixelSize: 4, paletteSize: 32, steps: 25 },
            'gameboy': { pixelSize: 6, paletteSize: 4, steps: 20 },
            'minimal': { pixelSize: 16, paletteSize: 8, steps: 15 }
        };
        
        const preset = presets[presetName];
        if (preset) {
            // 値を設定
            this.elements.pixelSize.value = preset.pixelSize;
            this.elements.paletteSize.value = preset.paletteSize;
            this.elements.steps.value = preset.steps;
            
            // 表示を更新
            this.elements.pixelSizeValue.textContent = preset.pixelSize;
            this.elements.paletteSizeValue.textContent = preset.paletteSize + '色';
            this.elements.stepsValue.textContent = preset.steps;
        }
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.showToast('サーバーに接続しました', 'success');
            }
        } catch (error) {
            this.showToast('サーバーに接続できません', 'error');
            console.error('Server health check failed:', error);
        }
    }
    
    async generateImage() {
        const prompt = this.elements.prompt.value.trim();
        if (!prompt) {
            this.showToast('プロンプトを入力してください', 'warning');
            return;
        }
        
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.startTime = Date.now();
        this.showProgress();
        
        const size = parseInt(this.elements.imageSize.value);
        const params = {
            prompt: prompt,
            negative_prompt: this.elements.negativePrompt.value,
            model_id: this.elements.model.value,
            width: size,
            height: size,
            steps: parseInt(this.elements.steps.value),
            guidance_scale: 7.5,
            pixel_size: parseInt(this.elements.pixelSize.value),
            palette_size: parseInt(this.elements.paletteSize.value)
        };
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResult(data.image);
                this.showToast('ピクセルアートが生成されました！', 'success');
            } else {
                throw new Error(data.error || '生成に失敗しました');
            }
        } catch (error) {
            this.showToast(`エラー: ${error.message}`, 'error');
            console.error('Generation error:', error);
            this.hideProgress();
        } finally {
            this.isGenerating = false;
        }
    }
    
    async generateSpriteSheet() {
        const prompt = this.elements.prompt.value.trim();
        if (!prompt) {
            this.showToast('プロンプトを入力してください', 'warning');
            return;
        }
        
        if (this.isGenerating) return;
        
        this.isGenerating = true;
        this.startTime = Date.now();
        this.showProgress('4方向スプライトシートを生成中...');
        
        const params = {
            prompt: prompt,
            model_id: 'Onodofthenorth/SD_PixelArt_SpriteSheet_Generator',
            negative_prompt: this.elements.negativePrompt.value
        };
        
        try {
            const response = await fetch('/generate_sprite_sheet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResult(data.image);
                this.showToast('スプライトシートが生成されました！', 'success');
            } else {
                throw new Error(data.error || '生成に失敗しました');
            }
        } catch (error) {
            this.showToast(`エラー: ${error.message}`, 'error');
            console.error('Sprite sheet generation error:', error);
            this.hideProgress();
        } finally {
            this.isGenerating = false;
        }
    }
    
    showGlitchModal() {
        this.elements.glitchModal.show();
    }
    
    async generateGlitchArt() {
        this.elements.glitchModal.hide();
        
        this.isGenerating = true;
        this.startTime = Date.now();
        this.showProgress('グリッチアートを生成中...');
        
        const params = {
            style: this.elements.glitchStyle.value,
            pixel_size: parseInt(this.elements.glitchPixelSize.value),
            animated: this.elements.glitchAnimation.checked,
            width: 512,
            height: 512
        };
        
        try {
            const response = await fetch('/generate_glitch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResult(data.image);
                this.showToast('グリッチアートが生成されました！', 'success');
            } else {
                throw new Error(data.error || '生成に失敗しました');
            }
        } catch (error) {
            this.showToast(`エラー: ${error.message}`, 'error');
            console.error('Glitch art generation error:', error);
            this.hideProgress();
        } finally {
            this.isGenerating = false;
        }
    }
    
    showProgress(message = '生成中...') {
        this.elements.placeholder.style.display = 'none';
        this.elements.result.style.display = 'none';
        this.elements.progress.style.display = 'block';
        this.elements.progressMessage.textContent = message;
        
        // 経過時間を表示
        this.progressInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            this.elements.progressTime.textContent = `${elapsed}秒経過`;
        }, 1000);
        
        this.elements.generateBtn.disabled = true;
    }
    
    hideProgress() {
        this.elements.progress.style.display = 'none';
        this.elements.generateBtn.disabled = false;
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }
    
    displayResult(imageData) {
        this.hideProgress();
        this.currentImage = imageData;
        
        this.elements.result.style.display = 'flex';
        this.elements.resultImage.src = imageData;
        this.elements.imageControls.style.display = 'flex';
    }
    
    async downloadImage() {
        if (!this.currentImage) return;
        
        const link = document.createElement('a');
        link.href = this.currentImage;
        link.download = `pixa_${Date.now()}.png`;
        link.click();
        
        this.showToast('画像をダウンロードしました', 'success');
    }
    
    async copyImage() {
        if (!this.currentImage) return;
        
        try {
            const blob = await fetch(this.currentImage).then(r => r.blob());
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
            ]);
            this.showToast('画像をコピーしました', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            this.showToast('コピーに失敗しました', 'error');
        }
    }
    
    async shareImage() {
        if (!this.currentImage) return;
        
        if (navigator.share) {
            try {
                const blob = await fetch(this.currentImage).then(r => r.blob());
                const file = new File([blob], 'pixel-art.png', { type: 'image/png' });
                
                await navigator.share({
                    title: 'Pixa - AIピクセルアート',
                    text: 'AIで生成したピクセルアート',
                    files: [file]
                });
            } catch (error) {
                console.error('Share failed:', error);
            }
        } else {
            this.showToast('共有機能はこのブラウザではサポートされていません', 'warning');
        }
    }
    
    animateImage() {
        // アニメーション機能の実装（将来的に）
        this.showToast('アニメーション機能は準備中です', 'info');
    }
    
    showToast(message, type = 'success') {
        const toast = this.elements.toast;
        const icon = toast.querySelector('i');
        
        // アイコンクラスを更新
        icon.className = type === 'success' ? 'fas fa-check-circle text-success' : 
                       type === 'warning' ? 'fas fa-exclamation-circle text-warning' : 
                       type === 'error' ? 'fas fa-times-circle text-danger' :
                       'fas fa-info-circle text-info';
        
        this.elements.toastMessage.textContent = message;
        toast.style.display = 'flex';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
}

// アプリケーションの初期化
document.addEventListener('DOMContentLoaded', () => {
    window.pixelArtGenerator = new PixelArtGeneratorImproved();
});