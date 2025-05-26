/**
 * Pixa - メインアプリケーション (リファクタリング版)
 */
class PixaApp {
    constructor() {
        this.currentMode = 'pixel-art';
        
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

        // 生成ボタン
        document.getElementById('generate-btn').addEventListener('click', () => {
            this.generate();
        });

        // 最適化GIFボタン
        const optimizedBtns = ['optimized-gif-btn', 'single-optimized-gif-btn'];
        optimizedBtns.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => this.generateOptimizedAnimation());
            }
        });

        // 一括最適化GIFボタン
        const batchBtns = ['batch-optimized-gif-btn', 'batch-optimized-gif-btn-settings'];
        batchBtns.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => this.batchGenerateOptimizedAnimations());
            }
        });

        // ツールバーボタン
        this.setupToolbarButtons();
        
        // レンジスライダー更新
        this.setupRangeSliders();

        // プロンプト入力
        this.setupPromptInput();
    }

    setupToolbarButtons() {
        const buttons = [
            { id: 'save-btn', handler: () => this.saveImage() },
            { id: 'copy-btn', handler: () => this.copyImage() },
            { id: 'share-btn', handler: () => this.shareImage() }
        ];

        buttons.forEach(({ id, handler }) => {
            const btn = document.getElementById(id);
            if (btn) btn.addEventListener('click', handler);
        });
    }

    setupRangeSliders() {
        document.querySelectorAll('input[type="range"]').forEach(range => {
            range.addEventListener('input', (e) => {
                const valueSpan = document.getElementById(e.target.id + '-value');
                if (valueSpan) {
                    valueSpan.textContent = e.target.value;
                }
            });
        });
    }

    setupPromptInput() {
        const promptInput = document.getElementById('prompt');
        if (promptInput) {
            promptInput.addEventListener('input', () => {
                this.updateCharCounter();
            });
        }

        // クイックプロンプト
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                if (promptInput) {
                    promptInput.value = prompt;
                    this.updateCharCounter();
                }
            });
        });
    }

    /**
     * モード切り替え
     */
    switchMode(mode) {
        this.currentMode = mode;

        // タブの更新
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });

        this.updateModeSettings();
    }

    updateModeSettings() {
        // モード別設定の表示/非表示
        document.querySelectorAll('.mode-style-settings').forEach(settings => {
            settings.style.display = 'none';
        });

        const activeSettings = document.getElementById(`${this.currentMode}-style-settings`);
        if (activeSettings) {
            activeSettings.style.display = 'block';
        }
    }

    /**
     * 基本画像生成
     */
    async generate() {
        if (uiService.isGenerating) return;

        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt) {
            uiService.showToast('プロンプトを入力してください', 'error');
            return;
        }

        uiService.setGeneratingState(true);
        uiService.simulateProgress();

        try {
            const params = this.getGenerationParams(prompt);
            const data = await apiService.generateImage(params);

            if (data.success) {
                uiService.displayImage(data.image);
                uiService.addToHistory(data.image, this.currentMode);
                uiService.showToast('生成が完了しました！', 'success');
            } else {
                throw new Error(data.error || '生成に失敗しました');
            }

        } catch (error) {
            console.error('Generation error:', error);
            uiService.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            uiService.setGeneratingState(false);
        }
    }

    /**
     * 最適化GIF生成
     */
    async generateOptimizedAnimation() {
        if (uiService.isGenerating) return;

        const currentImage = uiService.getCurrentImage();
        if (!currentImage) {
            uiService.showToast('まず画像を生成してください', 'error');
            return;
        }

        uiService.setGeneratingState(true);
        uiService.simulateProgress();

        try {
            const params = this.getOptimizationParams(currentImage);
            const data = await apiService.generateOptimizedAnimation(params);

            if (data.success) {
                uiService.displayImage(data.image);
                uiService.addToHistory(data.image, 'optimized-animation');
                
                const sizeInfo = data.file_size_kb ? ` (${data.file_size_kb}KB)` : '';
                uiService.showToast(`最適化GIF生成完了！${sizeInfo}`, 'success');
            } else {
                throw new Error(data.error || '最適化GIF生成に失敗しました');
            }

        } catch (error) {
            console.error('Optimized Animation error:', error);
            uiService.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            uiService.setGeneratingState(false);
        }
    }

    /**
     * 一括最適化GIF生成
     */
    async batchGenerateOptimizedAnimations() {
        if (uiService.isGenerating) return;

        const currentImage = uiService.getCurrentImage();
        if (!currentImage) {
            uiService.showToast('まず画像を生成してください', 'error');
            return;
        }

        uiService.setGeneratingState(true);
        uiService.simulateProgress();

        try {
            const params = {
                existing_image: currentImage,
                pixel_size: parseInt(document.getElementById('pixel-size')?.value || 8),
                palette_size: parseInt(document.getElementById('palette-size')?.value || 16)
            };

            const data = await apiService.batchGenerateOptimizedAnimations(params);

            if (data.success) {
                this.showBatchAnimationResults(data);
                
                const stats = data.statistics;
                uiService.showToast(
                    `一括生成完了！ ${stats.success_count}/${stats.total_count} アニメーション`,
                    'success'
                );
            } else {
                throw new Error(data.error || '一括最適化GIF生成に失敗しました');
            }

        } catch (error) {
            console.error('Batch Optimized Animations error:', error);
            uiService.showToast('エラーが発生しました: ' + error.message, 'error');
        } finally {
            uiService.setGeneratingState(false);
        }
    }

    /**
     * 生成パラメータを取得
     */
    getGenerationParams(prompt) {
        return {
            prompt: prompt,
            negative_prompt: document.getElementById('negative-prompt')?.value || '',
            model_id: document.getElementById('model')?.value || 'runwayml/stable-diffusion-v1-5',
            pixel_size: parseInt(document.getElementById('pixel-size')?.value || 8),
            palette_size: parseInt(document.getElementById('palette-size')?.value || 16),
            width: 512,
            height: 512
        };
    }

    /**
     * 最適化パラメータを取得
     */
    getOptimizationParams(imageData) {
        return {
            existing_image: imageData,
            animation_type: document.getElementById('optimized-animation-type')?.value || 'heartbeat',
            frame_count: parseInt(document.getElementById('optimized-frame-count')?.value || 8),
            tolerance: parseInt(document.getElementById('optimization-tolerance')?.value || 3),
            duration: parseInt(document.getElementById('animation-duration')?.value || 100),
            pixel_size: parseInt(document.getElementById('pixel-size')?.value || 8),
            palette_size: parseInt(document.getElementById('palette-size')?.value || 16)
        };
    }

    /**
     * 一括結果モーダル表示
     */
    showBatchAnimationResults(data) {
        const modal = this.createBatchResultsModal(data);
        document.body.appendChild(modal);
    }

    createBatchResultsModal(data) {
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
                        ${this.renderAnimationResults(data.animations)}
                    </div>
                </div>
            </div>
        `;

        // モーダルイベント
        this.setupModalEvents(modal);

        return modal;
    }

    renderAnimationResults(animations) {
        return Object.entries(animations).map(([type, result]) => {
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
        }).join('');
    }

    setupModalEvents(modal) {
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

    /**
     * アニメーションを使用
     */
    useAnimation(imageData) {
        uiService.displayImage(imageData);
        uiService.addToHistory(imageData, 'optimized-animation');
        uiService.showToast('アニメーションが設定されました', 'success');

        const modal = document.querySelector('.batch-results-modal');
        if (modal) {
            document.body.removeChild(modal);
        }
    }

    // その他のメソッド（保存、コピー、共有など）は簡略化
    saveImage() { /* 実装 */ }
    copyImage() { /* 実装 */ }
    shareImage() { /* 実装 */ }
    updateCharCounter() { /* 実装 */ }
    loadSettings() { /* 実装 */ }
}

// アプリケーション初期化
const pixaApp = new PixaApp();
