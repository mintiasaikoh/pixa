// Modern UI JavaScript for Pixa
class PixaApp {
    constructor() {
        this.currentMode = 'pixel-art';
        this.imageHistory = [];
        this.isGenerating = false;
        this.currentImage = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.updateModeSettings();
    }
    
    setupEventListeners() {
        // モード切り替え
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });
        
        // クイックプロンプト
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                document.getElementById('prompt').value = prompt;
                this.updateCharCounter();
            });
        });
        
        // プロンプト文字数カウンター
        document.getElementById('prompt').addEventListener('input', () => {
            this.updateCharCounter();
        });
        
        // 生成ボタン
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.generate();
        });
        
        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.generate();
            }
        });
        
        // ツールバーボタン
        document.getElementById('zoom-in').addEventListener('click', () => this.zoom(1.2));
        document.getElementById('zoom-out').addEventListener('click', () => this.zoom(0.8));
        document.getElementById('zoom-fit').addEventListener('click', () => this.zoomFit());
        
        document.getElementById('save-btn').addEventListener('click', () => this.saveImage());
        document.getElementById('copy-btn').addEventListener('click', () => this.copyImage());
        document.getElementById('share-btn').addEventListener('click', () => this.shareImage());
        
        // 差分合成最適化GIFボタン
        document.getElementById('optimized-gif-btn').addEventListener('click', () => {
            this.generateOptimizedAnimation();
        });
        document.getElementById('batch-optimized-gif-btn').addEventListener('click', () => {
            this.batchGenerateOptimizedAnimations();
        });
        document.getElementById('single-optimized-gif-btn').addEventListener('click', () => {
            this.generateOptimizedAnimation();
        });
        document.getElementById('batch-optimized-gif-btn-settings').addEventListener('click', () => {
            this.batchGenerateOptimizedAnimations();
        });
        
        // レンジスライダー更新
        document.querySelectorAll('input[type="range"]').forEach(range => {
            range.addEventListener('input', (e) => {
                const valueSpan = document.getElementById(e.target.id + '-value');
                if (valueSpan) {
                    valueSpan.textContent = e.target.value;
                }
            });
        });
        
        // アニメーションタイプ選択
        document.querySelectorAll('.animation-type-card').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('.animation-type-card').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
            });
        });
        
        // 履歴パネル
        document.getElementById('history-btn').addEventListener('click', () => {
            document.getElementById('history-panel').classList.toggle('collapsed');
        });
        
        // プロンプトクリア
        document.getElementById('clear-prompt').addEventListener('click', () => {
            document.getElementById('prompt').value = '';
            this.updateCharCounter();
        });
        
        // AI強化（実装予定）
        document.getElementById('magic-enhance').addEventListener('click', () => {
            this.showToast('AI強化機能は近日公開予定です', 'info');
        });
    }
    
    switchMode(mode) {
        this.currentMode = mode;
        
        // タブの更新
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        // 設定パネルの更新
        this.updateModeSettings();
        
        // モードタイトルの更新
        const titleMap = {
            'pixel-art': 'ピクセルアートスタイル',
            'glitch-art': 'グリッチアートスタイル',
            'animation': 'アニメーションスタイル'
        };
        
        const modeTitle = document.getElementById('mode-style-title');
        if (modeTitle) {
            modeTitle.textContent = titleMap[mode] || 'スタイル設定';
        }
        
        // ボタンテキストの更新
        const generateBtn = document.getElementById('generate-btn');
        const btnText = generateBtn.querySelector('.button-content');
        
        switch(mode) {
            case 'pixel-art':
                btnText.innerHTML = '<i class="fas fa-magic me-2"></i>生成する';
                break;
            case 'glitch-art':
                btnText.innerHTML = '<i class="fas fa-bolt me-2"></i>グリッチアートを生成';
                break;
            case 'animation':
                btnText.innerHTML = '<i class="fas fa-film me-2"></i>アニメーションを生成';
                break;
        }
    }
    
    updateModeSettings() {
        // 旧設定グループを非表示（互換性のため）
        document.querySelectorAll('.settings-group').forEach(group => {
            group.style.display = 'none';
        });
        
        // 統合UIのモード別設定を更新
        document.querySelectorAll('.mode-style-settings').forEach(settings => {
            settings.style.display = 'none';
        });
        
        // 現在のモードの設定を表示
        const modeMap = {
            'pixel-art': 'pixel',
            'glitch-art': 'glitch',
            'animation': 'animation'
        };
        
        const styleSettingsId = `${modeMap[this.currentMode] || this.currentMode}-style-settings`;
        const styleSettings = document.getElementById(styleSettingsId);
        if (styleSettings) {
            styleSettings.style.display = 'block';
        }
        
        // 旧UIの設定も表示（互換性のため）
        const settingsId = this.currentMode + '-settings';
        const settings = document.getElementById(settingsId);
        if (settings) {
            settings.style.display = 'block';
        }
    }
    
    updateCharCounter() {
        const prompt = document.getElementById('prompt');
        const counter = document.getElementById('prompt-length');
        counter.textContent = prompt.value.length;
    }
    
    async generate() {
        if (this.isGenerating) return;
        
        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt) {
            this.showToast('プロンプトを入力してください', 'error');
            return;
        }
        
        this.isGenerating = true;
        this.setGeneratingState(true);
        
        try {
            let endpoint;
            const params = {
                prompt: prompt,
                negative_prompt: document.getElementById('negative-prompt').value,
                model_id: document.getElementById('model').value
            };
            
            switch(this.currentMode) {
                case 'pixel-art':
                    endpoint = '/generate';
                    params.pixel_size = parseInt(document.getElementById('pixel-size').value);
                    params.palette_size = parseInt(document.getElementById('palette-size').value);
                    params.steps = parseInt(document.getElementById('steps')?.value || 20);
                    params.guidance_scale = parseFloat(document.getElementById('cfg-scale')?.value || 7);
                    break;
                    
                case 'glitch-art':
                    endpoint = '/generate_glitch_art';
                    params.pixel_size = parseInt(document.getElementById('glitch-pixel-size').value);
                    break;
                    
                case 'animation':
                    endpoint = '/generate_animation';
                    params.animation_type = document.querySelector('.animation-type-card.selected').dataset.type;
                    params.frame_count = parseInt(document.getElementById('frame-count').value);
                    params.fps = parseInt(document.getElementById('fps').value);
                    break;
            }
            
            // 進行状況のシミュレーション
            this.simulateProgress();
            
            const response = await fetch(`http://localhost:5001${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error('生成に失敗しました');
            }
            
            const data = await response.json();
            console.log('API Response:', data); // デバッグ用
            
            // 画像データの処理
            let imageData = data.image || data.animation;
            if (!imageData) {
                throw new Error('画像データが見つかりません');
            }
            
            // APIは既にdata:image形式で返しているのでそのまま使用
            this.displayImage(imageData);
            this.addToHistory(imageData, this.currentMode);
            this.showToast('生成が完了しました！', 'success');
            
        } catch (error) {
            console.error('Generation error:', error);
            this.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState(false);
        }
    }
    
    simulateProgress() {
        let progress = 0;
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 95) progress = 95;
            
            progressFill.style.width = progress + '%';
            progressText.textContent = Math.floor(progress) + '%';
            
            if (!this.isGenerating) {
                progressFill.style.width = '100%';
                progressText.textContent = '100%';
                clearInterval(interval);
            }
        }, 300);
    }
    
    setGeneratingState(isGenerating) {
        document.getElementById('empty-state').style.display = isGenerating || this.currentImage ? 'none' : 'block';
        document.getElementById('generating-state').style.display = isGenerating ? 'block' : 'none';
        document.getElementById('image-viewer').style.display = !isGenerating && this.currentImage ? 'block' : 'none';
        
        const generateBtn = document.getElementById('generate-btn');
        generateBtn.disabled = isGenerating;
        generateBtn.querySelector('.button-content').style.display = isGenerating ? 'none' : 'flex';
        generateBtn.querySelector('.button-loader').style.display = isGenerating ? 'flex' : 'none';
        
        // ツールバーボタンの状態
        const hasImage = !isGenerating && this.currentImage;
        document.getElementById('save-btn').disabled = !hasImage;
        document.getElementById('copy-btn').disabled = !hasImage;
        document.getElementById('share-btn').disabled = !hasImage;
        document.getElementById('optimized-gif-btn').disabled = !hasImage;
        document.getElementById('batch-optimized-gif-btn').disabled = !hasImage;
        document.getElementById('single-optimized-gif-btn').disabled = !hasImage;
        document.getElementById('batch-optimized-gif-btn-settings').disabled = !hasImage;
    }

    // 差分合成最適化GIF生成
    async generateOptimizedAnimation() {
        if (this.isGenerating) return;
        
        if (!this.currentImage) {
            this.showToast('まず画像を生成してください', 'error');
            return;
        }
        
        this.isGenerating = true;
        this.setGeneratingState(true);
        
        try {
            const animationType = document.getElementById('optimized-animation-type')?.value || 'heartbeat';
            const frameCount = parseInt(document.getElementById('optimized-frame-count')?.value || 8);
            const tolerance = parseInt(document.getElementById('optimization-tolerance')?.value || 3);
            const duration = parseInt(document.getElementById('animation-duration')?.value || 100);
            
            const params = {
                existing_image: this.currentImage,
                animation_type: animationType,
                frame_count: frameCount,
                pixel_size: parseInt(document.getElementById('pixel-size')?.value || 8),
                palette_size: parseInt(document.getElementById('palette-size')?.value || 16),
                tolerance: tolerance,
                duration: duration
            };
            
            // 進行状況のシミュレーション
            this.simulateProgress();
            
            const response = await fetch('http://localhost:5001/generate_optimized_animation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error('最適化GIF生成に失敗しました');
            }
            
            const data = await response.json();
            console.log('Optimized Animation Response:', data);
            
            if (data.success) {
                this.displayImage(data.image);
                this.addToHistory(data.image, 'optimized-animation');
                
                const sizeInfo = data.file_size_kb ? ` (${data.file_size_kb}KB)` : '';
                this.showToast(`差分合成最適化GIF生成完了！${sizeInfo}`, 'success');
            } else {
                throw new Error(data.error || '最適化GIF生成に失敗しました');
            }
            
        } catch (error) {
            console.error('Optimized Animation error:', error);
            this.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState(false);
        }
    }

    // 一括最適化GIF生成
    async batchGenerateOptimizedAnimations() {
        if (this.isGenerating) return;
        
        if (!this.currentImage) {
            this.showToast('まず画像を生成してください', 'error');
            return;
        }
        
        this.isGenerating = true;
        this.setGeneratingState(true);
        
        try {
            const params = {
                existing_image: this.currentImage,
                pixel_size: parseInt(document.getElementById('pixel-size')?.value || 8),
                palette_size: parseInt(document.getElementById('palette-size')?.value || 16)
            };
            
            const response = await fetch('http://localhost:5001/batch_generate_optimized_animations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error('一括最適化GIF生成に失敗しました');
            }
            
            const data = await response.json();
            console.log('Batch Optimized Animations Response:', data);
            
            if (data.success) {
                this.showBatchAnimationResults(data);
                const stats = data.statistics;
                this.showToast(
                    `一括生成完了！ ${stats.success_count}/${stats.total_count} アニメーション (合計${stats.total_size_kb}KB)`,
                    'success'
                );
            } else {
                throw new Error(data.error || '一括最適化GIF生成に失敗しました');
            }
            
        } catch (error) {
            console.error('Batch Optimized Animations error:', error);
            this.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState(false);
        }
    }

    // 一括アニメーション結果の表示
    showBatchAnimationResults(data) {
        const modal = document.createElement('div');
        modal.className = 'batch-results-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>一括最適化GIF生成結果</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="batch-stats">
                        <p>成功: ${data.statistics.success_count}/${data.statistics.total_count}</p>
                        <p>合計サイズ: ${data.statistics.total_size_kb}KB</p>
                        <p>平均サイズ: ${data.statistics.average_size_kb}KB</p>
                    </div>
                    <div class="animation-grid">
                        ${Object.entries(data.animations).map(([type, result]) => {
                            if (result.success) {
                                return `
                                    <div class="animation-result">
                                        <div class="animation-preview">
                                            <img src="${result.image}" alt="${type}" />
                                        </div>
                                        <div class="animation-info">
                                            <h4>${type}</h4>
                                            <p>${result.file_size_kb}KB</p>
                                            <button class="btn-secondary" onclick="pixaApp.useAnimation('${result.image}')">使用</button>
                                        </div>
                                    </div>
                                `;
                            } else {
                                return `
                                    <div class="animation-result error">
                                        <h4>${type}</h4>
                                        <p class="error-text">${result.error}</p>
                                    </div>
                                `;
                            }
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // モーダルを閉じる
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    // アニメーションを使用
    useAnimation(imageData) {
        this.displayImage(imageData);
        this.addToHistory(imageData, 'optimized-animation');
        this.showToast('アニメーションが設定されました', 'success');
        
        const modal = document.querySelector('.batch-results-modal');
        if (modal) {
            document.body.removeChild(modal);
        }
    }
    
    displayImage(imageData) {
        this.currentImage = imageData;
        const img = document.getElementById('generated-image');
        
        // APIが既に data:image 形式で返しているのでそのまま使用
        img.src = imageData;
        
        img.onload = () => {
            document.getElementById('image-dimensions').textContent = 
                `${img.naturalWidth} × ${img.naturalHeight}px`;
        };
        
        this.setGeneratingState(false);
    }
    
    addToHistory(imageData, type) {
        this.imageHistory.unshift({
            image: imageData,
            type: type,
            timestamp: new Date(),
            prompt: document.getElementById('prompt').value
        });
        
        // 最大50件まで保持
        if (this.imageHistory.length > 50) {
            this.imageHistory.pop();
        }
        
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const grid = document.getElementById('history-grid');
        grid.innerHTML = '';
        
        this.imageHistory.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <img src="${item.image}" alt="履歴画像">
                <div class="history-item-type">${this.getTypeLabel(item.type)}</div>
            `;
            div.addEventListener('click', () => {
                this.displayImage(item.image);
                document.getElementById('prompt').value = item.prompt;
                this.updateCharCounter();
            });
            grid.appendChild(div);
        });
    }
    
    getTypeLabel(type) {
        const labels = {
            'pixel-art': 'ピクセル',
            'glitch-art': 'グリッチ',
            'animation': 'アニメ'
        };
        return labels[type] || type;
    }
    
    // ズーム機能
    zoom(factor) {
        const img = document.getElementById('generated-image');
        const currentScale = img.style.transform ? 
            parseFloat(img.style.transform.match(/scale\(([\d.]+)\)/)?.[1] || 1) : 1;
        const newScale = currentScale * factor;
        img.style.transform = `scale(${newScale})`;
        document.querySelector('.zoom-level').textContent = Math.round(newScale * 100) + '%';
    }
    
    zoomFit() {
        const img = document.getElementById('generated-image');
        img.style.transform = 'scale(1)';
        document.querySelector('.zoom-level').textContent = '100%';
    }
    
    // 画像保存
    async saveImage() {
        if (!this.currentImage) return;
        
        const link = document.createElement('a');
        link.download = `pixa_${Date.now()}.png`;
        link.href = this.currentImage; // 既にdata:image形式
        link.click();
        
        this.showToast('画像を保存しました', 'success');
    }
    
    // クリップボードにコピー
    async copyImage() {
        if (!this.currentImage) return;
        
        try {
            const blob = await (await fetch(this.currentImage)).blob();
            await navigator.clipboard.write([
                new ClipboardItem({ 'image/png': blob })
            ]);
            this.showToast('クリップボードにコピーしました', 'success');
        } catch (err) {
            this.showToast('コピーに失敗しました', 'error');
        }
    }
    
    // 共有
    async shareImage() {
        if (!this.currentImage) return;
        
        if (navigator.share) {
            try {
                const blob = await (await fetch(this.currentImage)).blob();
                const file = new File([blob], 'pixa.png', { type: 'image/png' });
                await navigator.share({
                    title: 'Pixaで生成した画像',
                    text: document.getElementById('prompt').value,
                    files: [file]
                });
            } catch (err) {
                console.log('Share failed:', err);
            }
        } else {
            this.showToast('お使いのブラウザでは共有機能が利用できません', 'info');
        }
    }
    
    // トースト通知
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type]} toast-icon"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        `;
        
        container.appendChild(toast);
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => toast.remove());
        
        // 3秒後に自動削除
        setTimeout(() => toast.remove(), 3000);
    }
    
    // 設定の保存と読み込み
    saveSettings() {
        const settings = {
            pixelSize: document.getElementById('pixel-size').value,
            paletteSize: document.getElementById('palette-size').value,
            steps: document.getElementById('steps').value,
            cfgScale: document.getElementById('cfg-scale').value
        };
        localStorage.setItem('pixaSettings', JSON.stringify(settings));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('pixaSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            if (settings.pixelSize) {
                document.getElementById('pixel-size').value = settings.pixelSize;
                document.getElementById('pixel-size-value').textContent = settings.pixelSize;
            }
            if (settings.paletteSize) {
                document.getElementById('palette-size').value = settings.paletteSize;
                document.getElementById('palette-size-value').textContent = settings.paletteSize;
            }
            if (settings.steps) {
                document.getElementById('steps').value = settings.steps;
            }
            if (settings.cfgScale) {
                document.getElementById('cfg-scale').value = settings.cfgScale;
            }
        }
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    window.pixaApp = new PixaApp();
});
