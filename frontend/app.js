/**
 * AI ピクセルアート ジェネレーター - フロントエンド JavaScript
 */

class PixelArtGenerator {
    constructor() {
        this.apiUrl = '';
        this.isGenerating = false;
        this.currentImage = null;
        this.currentAnimation = null;
        this.savedImageForAnimation = null;
        this.lastGenerationParams = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadPresets();
        this.checkServerStatus();
    }
    
    initializeElements() {
        // DOM要素を取得
        this.elements = {
            prompt: document.getElementById('prompt'),
            negativePrompt: document.getElementById('negative-prompt'),
            preset: document.getElementById('preset'),
            width: document.getElementById('width'),
            height: document.getElementById('height'),
            pixelSize: document.getElementById('pixel-size'),
            pixelSizeValue: document.getElementById('pixel-size-value'),
            paletteSize: document.getElementById('palette-size'),
            paletteSizeValue: document.getElementById('palette-size-value'),
            steps: document.getElementById('steps'),
            stepsValue: document.getElementById('steps-value'),
            guidance: document.getElementById('guidance'),
            guidanceValue: document.getElementById('guidance-value'),
            seed: document.getElementById('seed'),
            generateBtn: document.getElementById('generate-btn'),
            progressContainer: document.getElementById('progress-container'),
            progressBar: document.getElementById('progress-bar'),
            progressText: document.getElementById('progress-text'),
            placeholder: document.getElementById('placeholder'),
            resultImage: document.getElementById('result-image'),
            imageControls: document.getElementById('image-controls'),
            downloadBtn: document.getElementById('download-btn'),
            copyBtn: document.getElementById('copy-btn'),
            animateBtn: document.getElementById('animate-btn'),
            generationInfo: document.getElementById('generation-info'),
            quickPrompts: document.querySelectorAll('.quick-prompt'),
            presetDescription: document.getElementById('preset-description'),
            // アニメーション関連
            animationType: document.getElementById('animation-type'),
            frameCount: document.getElementById('frame-count'),
            frameCountValue: document.getElementById('frame-count-value'),
            fps: document.getElementById('fps'),
            fpsValue: document.getElementById('fps-value'),
            generateAnimationBtn: document.getElementById('generate-animation-btn'),
            downloadGifBtn: document.getElementById('download-gif-btn'),
            animationStatus: document.getElementById('animation-status'),
            animationStatusText: document.getElementById('animation-status-text'),
            newImageBtn: document.getElementById('new-image-btn')
        };
    }
    
    bindEvents() {
        // 生成ボタン
        this.elements.generateBtn.addEventListener('click', () => this.generateImage());
        
        // Enterキーで生成
        this.elements.prompt.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.generateImage();
            }
        });
        
        // レンジスライダーの値表示更新
        this.elements.pixelSize.addEventListener('input', (e) => {
            this.elements.pixelSizeValue.textContent = e.target.value;
        });
        
        this.elements.paletteSize.addEventListener('input', (e) => {
            this.elements.paletteSizeValue.textContent = e.target.value;
        });
        
        this.elements.steps.addEventListener('input', (e) => {
            this.elements.stepsValue.textContent = e.target.value;
        });
        
        this.elements.guidance.addEventListener('input', (e) => {
            this.elements.guidanceValue.textContent = e.target.value;
        });
        
        this.elements.frameCount.addEventListener('input', (e) => {
            this.elements.frameCountValue.textContent = e.target.value + 'コマ';
        });
        
        this.elements.fps.addEventListener('input', (e) => {
            this.elements.fpsValue.textContent = e.target.value;
        });
        
        // プリセット変更
        this.elements.preset.addEventListener('change', (e) => {
            this.applyPreset(e.target.value);
            this.updatePresetDescription(e.target.value);
        });
        
        // ダウンロードボタン
        this.elements.downloadBtn.addEventListener('click', () => this.downloadImage());
        
        // コピーボタン
        this.elements.copyBtn.addEventListener('click', () => this.copyToClipboard());
        
        // アニメーション化ボタン
        this.elements.animateBtn.addEventListener('click', () => this.animateCurrentImage());
        
        // アニメーション生成ボタン
        this.elements.generateAnimationBtn.addEventListener('click', () => this.generateAnimation());
        
        // GIFダウンロードボタン
        this.elements.downloadGifBtn.addEventListener('click', () => this.downloadGif());
        
        // 新しい画像を生成ボタン
        this.elements.newImageBtn.addEventListener('click', () => this.resetToNewImage());
        
        // クイックプロンプト
        this.elements.quickPrompts.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.target.dataset.prompt;
                this.elements.prompt.value = prompt;
                this.elements.prompt.focus();
            });
        });
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy' && data.pipeline_loaded) {
                this.showStatus('サーバー接続成功', 'success');
            } else {
                this.showStatus('サーバーは動作していますが、AIモデルの読み込み中です', 'warning');
            }
        } catch (error) {
            this.showStatus('サーバーに接続できません。バックエンドが起動していることを確認してください。', 'error');
            this.elements.generateBtn.disabled = true;
        }
    }
    
    async loadPresets() {
        try {
            const response = await fetch(`${this.apiUrl}/presets`);
            const presets = await response.json();
            
            // プリセットオプションを追加
            for (const [key, preset] of Object.entries(presets)) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = preset.name;
                this.elements.preset.appendChild(option);
            }
            
            this.presets = presets;
        } catch (error) {
            console.error('プリセットの読み込みに失敗:', error);
        }
    }
    
    applyPreset(presetKey) {
        if (!presetKey || !this.presets || !this.presets[presetKey]) return;
        
        const preset = this.presets[presetKey];
        
        // UIにプリセット値を適用
        this.elements.pixelSize.value = preset.pixel_size;
        this.elements.pixelSizeValue.textContent = preset.pixel_size;
        
        this.elements.paletteSize.value = preset.palette_size;
        this.elements.paletteSizeValue.textContent = preset.palette_size;
        
        this.elements.steps.value = preset.steps;
        this.elements.stepsValue.textContent = preset.steps;
        
        this.elements.guidance.value = preset.guidance_scale;
        this.elements.guidanceValue.textContent = preset.guidance_scale;
    }
    
    updatePresetDescription(presetKey) {
        if (!presetKey) {
            this.elements.presetDescription.textContent = '';
            return;
        }
        
        if (this.presets && this.presets[presetKey] && this.presets[presetKey].description) {
            this.elements.presetDescription.textContent = this.presets[presetKey].description;
        } else {
            this.elements.presetDescription.textContent = '';
        }
    }
    
    async generateImage() {
        if (this.isGenerating) return;
        
        const prompt = this.elements.prompt.value.trim();
        if (!prompt) {
            this.showStatus('プロンプトを入力してください', 'error');
            return;
        }
        
        this.startGeneration();
        
        try {
            const params = this.getGenerationParams();
            
            const response = await fetch(`${this.apiUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResult(data.image, data.parameters);
                this.showStatus('生成完了！', 'success');
            } else {
                throw new Error(data.error || '生成に失敗しました');
            }
            
        } catch (error) {
            console.error('生成エラー:', error);
            this.showStatus(`エラー: ${error.message}`, 'error');
        } finally {
            this.endGeneration();
        }
    }
    
    getGenerationParams() {
        return {
            prompt: this.elements.prompt.value.trim(),
            negative_prompt: this.elements.negativePrompt.value.trim(),
            width: parseInt(this.elements.width.value),
            height: parseInt(this.elements.height.value),
            pixel_size: parseInt(this.elements.pixelSize.value),
            palette_size: parseInt(this.elements.paletteSize.value),
            steps: parseInt(this.elements.steps.value),
            guidance_scale: parseFloat(this.elements.guidance.value),
            seed: this.elements.seed.value ? parseInt(this.elements.seed.value) : null
        };
    }
    
    startGeneration() {
        this.isGenerating = true;
        this.elements.generateBtn.disabled = true;
        this.elements.generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>生成中...';
        
        this.elements.progressContainer.style.display = 'block';
        this.elements.progressBar.style.width = '0%';
        
        // プログレスアニメーション
        this.progressInterval = setInterval(() => {
            const currentWidth = parseFloat(this.elements.progressBar.style.width) || 0;
            if (currentWidth < 90) {
                this.elements.progressBar.style.width = (currentWidth + Math.random() * 10) + '%';
            }
        }, 500);
    }
    
    endGeneration() {
        this.isGenerating = false;
        this.elements.generateBtn.disabled = false;
        this.elements.generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>ピクセルアートを生成';
        
        this.elements.progressContainer.style.display = 'none';
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
    
    displayResult(imageData, parameters) {
        this.currentImage = imageData;
        this.currentAnimation = null;  // 静止画生成時はアニメーションをリセット
        this.lastGenerationParams = parameters; // パラメータを保存
        this.savedImageForAnimation = null; // 新しい画像が生成されたらアニメーション用の保存画像もリセット
        
        // アニメーション関連UIをリセット
        this.elements.animationStatus.style.display = 'none';
        this.elements.newImageBtn.style.display = 'none';
        
        // 画像を表示
        this.elements.resultImage.src = imageData;
        this.elements.resultImage.style.display = 'block';
        this.elements.placeholder.style.display = 'none';
        this.elements.imageControls.style.display = 'block';
        this.elements.downloadGifBtn.style.display = 'none';  // GIFダウンロードボタンを非表示
        
        // 生成情報を表示
        this.elements.generationInfo.innerHTML = `
            ${parameters.width}×${parameters.height}px<br>
            ピクセル: ${parameters.pixel_size}px<br>
            パレット: ${parameters.palette_size}色<br>
            ステップ: ${parameters.steps}<br>
            ${parameters.seed ? `シード: ${parameters.seed}` : 'ランダムシード'}
        `;
    }
    
    async generateAnimation() {
        if (this.isGenerating) return;
        
        // 保存された画像がある場合はそれを使用
        if (this.savedImageForAnimation) {
            this.startAnimationGeneration();
            
            try {
                const params = {
                    base_image: this.savedImageForAnimation.image,
                    prompt: this.savedImageForAnimation.params.prompt,
                    animation_type: this.elements.animationType.value,
                    frame_count: parseInt(this.elements.frameCount.value),
                    fps: parseInt(this.elements.fps.value),
                    width: this.savedImageForAnimation.params.width,
                    height: this.savedImageForAnimation.params.height,
                    pixel_size: this.savedImageForAnimation.params.pixel_size,
                    palette_size: this.savedImageForAnimation.params.palette_size
                };
                
                const response = await fetch(`${this.apiUrl}/animate_existing`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(params)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    this.displayAnimationResult(data.image, data);
                    this.showStatus('アニメーション生成完了！', 'success');
                    // savedImageForAnimationは保持し続ける（リセットしない）
                } else {
                    throw new Error(data.error || 'アニメーション生成に失敗しました');
                }
                
            } catch (error) {
                console.error('アニメーション生成エラー:', error);
                this.showStatus(`エラー: ${error.message}`, 'error');
            } finally {
                this.endAnimationGeneration();
            }
            return;
        }
        
        // 通常のアニメーション生成
        const prompt = this.elements.prompt.value.trim();
        if (!prompt) {
            this.showStatus('プロンプトを入力してください', 'error');
            return;
        }
        
        this.startAnimationGeneration();
        
        try {
            const params = {
                ...this.getGenerationParams(),
                animation_type: this.elements.animationType.value,
                frame_count: parseInt(this.elements.frameCount.value),
                fps: parseInt(this.elements.fps.value)
            };
            
            const response = await fetch(`${this.apiUrl}/generate_animation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.displayAnimationResult(data.image, data);
                this.showStatus('アニメーション生成完了！', 'success');
            } else {
                throw new Error(data.error || 'アニメーション生成に失敗しました');
            }
            
        } catch (error) {
            console.error('アニメーション生成エラー:', error);
            this.showStatus(`エラー: ${error.message}`, 'error');
        } finally {
            this.endAnimationGeneration();
        }
    }
    
    startAnimationGeneration() {
        this.isGenerating = true;
        this.elements.generateAnimationBtn.disabled = true;
        this.elements.generateAnimationBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>生成中...';
        
        this.elements.progressContainer.style.display = 'block';
        this.elements.progressBar.style.width = '0%';
        this.elements.progressText.textContent = 'アニメーション生成中...';
        
        // プログレスアニメーション
        this.progressInterval = setInterval(() => {
            const currentWidth = parseFloat(this.elements.progressBar.style.width) || 0;
            if (currentWidth < 90) {
                this.elements.progressBar.style.width = (currentWidth + Math.random() * 10) + '%';
            }
        }, 500);
    }
    
    endAnimationGeneration() {
        this.isGenerating = false;
        this.elements.generateAnimationBtn.disabled = false;
        this.elements.generateAnimationBtn.innerHTML = '<i class="fas fa-play-circle me-2"></i>アニメーションを生成';
        
        this.elements.progressContainer.style.display = 'none';
        this.elements.progressText.textContent = '生成中...';
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
    }
    
    displayAnimationResult(gifData, info) {
        this.currentAnimation = gifData;
        
        // GIFを表示
        this.elements.resultImage.src = gifData;
        this.elements.resultImage.style.display = 'block';
        this.elements.placeholder.style.display = 'none';
        this.elements.imageControls.style.display = 'block';
        this.elements.downloadGifBtn.style.display = 'inline-block';
        
        // 生成情報を表示
        this.elements.generationInfo.innerHTML = `
            アニメーション: ${info.animation_type}<br>
            フレーム数: ${info.frame_count}<br>
            FPS: ${info.fps}<br>
            ${info.message || ''}
        `;
    }
    
    downloadGif() {
        if (!this.currentAnimation) return;
        
        const link = document.createElement('a');
        link.href = this.currentAnimation;
        link.download = `pixel-animation-${Date.now()}.gif`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showStatus('GIFアニメーションをダウンロードしました', 'success');
    }
    
    downloadImage() {
        if (!this.currentImage) return;
        
        const link = document.createElement('a');
        link.href = this.currentImage;
        link.download = `pixel-art-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showStatus('画像をダウンロードしました', 'success');
    }
    
    async copyToClipboard() {
        if (!this.currentImage) {
            this.showStatus('コピーする画像がありません', 'error');
            return;
        }
        
        try {
            // Clipboard API対応チェック
            if (!navigator.clipboard || !navigator.clipboard.write) {
                throw new Error('Clipboard API not supported');
            }
            
            // HTTPS接続チェック（localhost以外）
            if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                throw new Error('Clipboard API requires HTTPS connection');
            }
            
            // Base64データの形式確認
            console.log('Current image data:', this.currentImage.substring(0, 50));
            
            // Base64データをBlobに変換
            const base64Data = this.currentImage.replace(/^data:image\/png;base64,/, '');
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            const blob = new Blob([bytes], { type: 'image/png' });
            console.log('Blob created:', blob.size, 'bytes');
            
            // クリップボードにコピー
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
            ]);
            
            this.showStatus('クリップボードにコピーしました', 'success');
            
        } catch (error) {
            console.error('コピーエラー:', error);
            
            // フォールバック: URLをコピー
            try {
                await navigator.clipboard.writeText(this.currentImage);
                this.showStatus('画像データURLをクリップボードにコピーしました', 'warning');
            } catch (fallbackError) {
                console.error('フォールバックも失敗:', fallbackError);
                this.showStatus(`コピーに失敗しました: ${error.message}`, 'error');
            }
        }
    }
    
    async animateCurrentImage() {
        if (!this.currentImage) {
            this.showStatus('アニメーション化する画像がありません', 'error');
            return;
        }
        
        // アニメーション設定アコーディオンを開く
        const animationCollapse = document.getElementById('animationCollapse');
        const bsCollapse = new bootstrap.Collapse(animationCollapse, {
            show: true
        });
        
        // アニメーション生成ボタンにフォーカス
        this.elements.generateAnimationBtn.scrollIntoView({ behavior: 'smooth' });
        
        // 現在の画像パラメータを保存
        this.savedImageForAnimation = {
            image: this.currentImage,
            params: this.lastGenerationParams
        };
        
        // ステータス表示
        this.elements.animationStatus.style.display = 'block';
        this.elements.animationStatusText.textContent = '選択された画像をアニメーション化できます';
        this.elements.newImageBtn.style.display = 'block';
        
        this.showStatus('アニメーション設定を調整して「アニメーションを生成」を押してください', 'info');
    }
    
    resetToNewImage() {
        // アニメーション化モードを解除
        this.savedImageForAnimation = null;
        this.elements.animationStatus.style.display = 'none';
        this.elements.newImageBtn.style.display = 'none';
        
        // アニメーション設定を閉じる
        const animationCollapse = document.getElementById('animationCollapse');
        const bsCollapse = new bootstrap.Collapse(animationCollapse, {
            hide: true
        });
        
        // プロンプト入力欄にフォーカス
        this.elements.prompt.focus();
        
        this.showStatus('新しい静止画を生成してください', 'info');
    }
    
    showStatus(message, type = 'info') {
        // 既存のアラートを削除
        const existingAlert = document.querySelector('.status-alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // アラートを作成
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show status-alert position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // 5秒後に自動削除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    new PixelArtGenerator();
});