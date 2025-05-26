/**
 * Pixa - UI管理サービス
 */
class UIService {
    constructor() {
        this.currentImage = null;
        this.imageHistory = [];
        this.isGenerating = false;
    }

    /**
     * 画像を表示
     */
    displayImage(imageData) {
        if (!imageData) return;

        this.currentImage = imageData;
        
        const imageElement = document.getElementById('generated-image');
        if (imageElement) {
            imageElement.src = imageData;
            imageElement.style.display = 'block';
        }

        // 画像情報を更新
        this.updateImageInfo(imageData);
        
        // 表示状態を更新
        this.updateDisplayState();
    }

    /**
     * 画像情報を更新
     */
    updateImageInfo(imageData) {
        if (!imageData) return;

        const dimensionsElement = document.getElementById('image-dimensions');
        if (dimensionsElement) {
            // 画像サイズを取得（簡易実装）
            const img = new Image();
            img.onload = () => {
                dimensionsElement.textContent = `${img.width} × ${img.height}`;
            };
            img.src = imageData;
        }
    }

    /**
     * 表示状態を更新
     */
    updateDisplayState() {
        const hasImage = !this.isGenerating && this.currentImage;
        
        // 各状態の表示/非表示
        this.toggleElement('empty-state', !hasImage && !this.isGenerating);
        this.toggleElement('generating-state', this.isGenerating);
        this.toggleElement('image-viewer', hasImage);

        // ツールバーボタンの状態
        this.updateToolbarButtons(hasImage);
    }

    /**
     * 要素の表示/非表示切り替え
     */
    toggleElement(elementId, show) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * ツールバーボタンの更新
     */
    updateToolbarButtons(hasImage) {
        const buttons = [
            'save-btn', 'copy-btn', 'share-btn', 
            'optimized-gif-btn', 'batch-optimized-gif-btn',
            'single-optimized-gif-btn', 'batch-optimized-gif-btn-settings'
        ];

        buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.disabled = !hasImage;
            }
        });
    }

    /**
     * 生成状態を設定
     */
    setGeneratingState(isGenerating) {
        this.isGenerating = isGenerating;
        
        // 生成ボタンの状態
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.disabled = isGenerating;
            
            const content = generateBtn.querySelector('.button-content');
            const loader = generateBtn.querySelector('.button-loader');
            
            if (content) content.style.display = isGenerating ? 'none' : 'flex';
            if (loader) loader.style.display = isGenerating ? 'flex' : 'none';
        }

        this.updateDisplayState();
    }

    /**
     * 進行状況をシミュレート
     */
    simulateProgress() {
        let progress = 0;
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');

        if (!progressFill || !progressText) return;

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

    /**
     * トースト通知を表示
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

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

        // 閉じるボタンのイベント
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => toast.remove());

        // 3秒後に自動削除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }

    /**
     * 履歴に追加
     */
    addToHistory(imageData, mode) {
        this.imageHistory.unshift({
            image: imageData,
            mode: mode,
            timestamp: new Date().toISOString()
        });

        // 履歴を最大20件に制限
        if (this.imageHistory.length > 20) {
            this.imageHistory = this.imageHistory.slice(0, 20);
        }
    }

    /**
     * 現在の画像を取得
     */
    getCurrentImage() {
        return this.currentImage;
    }

    /**
     * 履歴を取得
     */
    getHistory() {
        return this.imageHistory;
    }
}

/**
 * グローバルUIサービスインスタンス
 */
const uiService = new UIService();

// モジュールエクスポート
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UIService, uiService };
}
