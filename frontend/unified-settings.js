// 統合UI用の追加JavaScript - 修正版

// アコーディオン機能の初期化（修正版）
function initializeAccordion() {
    console.log('アコーディオン初期化開始');
    
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', (e) => {
            e.preventDefault();
            
            const target = header.getAttribute('data-target');
            const panel = document.getElementById(target);
            
            if (!panel) {
                console.error(`Panel not found: ${target}`);
                return;
            }
            
            // トグル処理
            const isActive = header.classList.contains('active');
            
            // 他のアコーディオンを閉じる（オプション）
            // document.querySelectorAll('.accordion-header').forEach(h => h.classList.remove('active'));
            // document.querySelectorAll('.accordion-panel').forEach(p => p.classList.remove('show'));
            
            // 現在のアコーディオンをトグル
            if (isActive) {
                header.classList.remove('active');
                panel.classList.remove('show');
            } else {
                header.classList.add('active');
                panel.classList.add('show');
            }
            
            console.log(`アコーディオン ${target} をトグル: ${!isActive}`);
        });
    });
}

// プロンプトテンプレート
const promptTemplates = {
    retro: [
        { emoji: '🎮', text: 'ファミコン風8ビットピクセルアート、シンプルな色使い', label: 'ファミコン風' },
        { emoji: '🌟', text: 'スーパーファミコン風16ビットピクセルアート、鮮やかな色彩', label: 'スーファミ風' },
        { emoji: '🟩', text: 'ゲームボーイ風モノクロ4階調ピクセルアート、緑がかった画面', label: 'ゲームボーイ風' },
        { emoji: '🕹️', text: 'アーケードゲーム風ピクセルアート、ネオンカラー、レトロフューチャー', label: 'アーケード風' }
    ]
};

// 品質プリセット機能（詳細説明付き）
const qualityPresets = {
    fast: {
        steps: 10,
        cfg_scale: 5,
        badge: '高速',
        badgeClass: 'warning',
        description: '数秒で生成・プレビュー向け'
    },
    standard: {
        steps: 20,
        cfg_scale: 7,
        badge: '標準',
        badgeClass: '',
        description: 'バランスの良い設定'
    },
    quality: {
        steps: 40,
        cfg_scale: 10,
        badge: '高品質',
        badgeClass: 'primary',
        description: '最高品質・時間がかかります'
    }
};

// プリセットボタンの初期化（改善版）
function initializePresets() {
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = btn.getAttribute('data-preset');
            const settings = qualityPresets[preset];
            
            if (settings) {
                // プリセットを適用
                const stepsInput = document.getElementById('steps');
                const cfgInput = document.getElementById('cfg-scale');
                
                if (stepsInput) {
                    stepsInput.value = settings.steps;
                    const stepsValue = document.getElementById('steps-value');
                    if (stepsValue) stepsValue.textContent = settings.steps;
                }
                
                if (cfgInput) {
                    cfgInput.value = settings.cfg_scale;
                    const cfgValue = document.getElementById('cfg-scale-value');
                    if (cfgValue) cfgValue.textContent = settings.cfg_scale.toFixed(1);
                }
                
                // バッジを更新
                const badge = document.querySelector('.quality-badge');
                if (badge) {
                    badge.textContent = settings.badge;
                    badge.className = `quality-badge ${settings.badgeClass}`;
                }
                
                // アクティブ状態を更新
                document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // 説明を表示
                showToast(`${settings.badge}モード: ${settings.description}`, 'info');
            }
        });
    });
}

// トースト通知機能
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const icons = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // アニメーション
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// その他の初期化関数...（省略）

// 統合設定の初期化（修正版）
function initializeUnifiedSettings() {
    console.log('統合設定の初期化開始');
    
    // アコーディオン初期化
    initializeAccordion();
    
    // プリセット初期化
    initializePresets();
    
    // その他の初期化
    initializeRandomSeed();
    initializeAspectRatio();
    initializeTooltips();
    initializeAnimationCards();
    
    // チップのイベントリスナーを追加（既存のものも含む）
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            const prompt = e.currentTarget.dataset.prompt;
            const promptInput = document.getElementById('prompt');
            if (promptInput) {
                promptInput.value = prompt;
                // 文字数カウンターを更新
                const event = new Event('input', { bubbles: true });
                promptInput.dispatchEvent(event);
                
                // レトロゲーム風スタイルの場合は特別な通知
                const label = e.currentTarget.textContent.trim();
                if (label.includes('風')) {
                    showToast(`${label}を選択しました！🎮`, 'success');
                }
            }
        });
    });
    
    console.log('統合設定の初期化完了');
}

// DOMContentLoadedで初期化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUnifiedSettings);
} else {
    // すでに読み込み済みの場合
    initializeUnifiedSettings();
}

// ランダムシード生成
function initializeRandomSeed() {
    const randomBtn = document.querySelector('.random-seed-btn');
    if (randomBtn) {
        randomBtn.addEventListener('click', () => {
            const randomSeed = Math.floor(Math.random() * 2147483647);
            const seedInput = document.getElementById('seed');
            if (seedInput) {
                seedInput.value = randomSeed;
                showToast(`シード値: ${randomSeed}`, 'info');
            }
        });
    }
}

// アスペクト比ボタンの初期化
function initializeAspectRatio() {
    document.querySelectorAll('.ratio-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.ratio-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const ratio = btn.dataset.ratio;
            showToast(`アスペクト比: ${ratio}`, 'info');
        });
    });
}

// インフォボタンのツールチップ
function initializeTooltips() {
    document.querySelectorAll('.info-btn').forEach(btn => {
        btn.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.title;
            document.body.appendChild(tooltip);
            
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = `${rect.left}px`;
            tooltip.style.top = `${rect.bottom + 5}px`;
            
            // 画面端でのはみ出しを防ぐ
            setTimeout(() => {
                const tooltipRect = tooltip.getBoundingClientRect();
                if (tooltipRect.right > window.innerWidth) {
                    tooltip.style.left = `${window.innerWidth - tooltipRect.width - 10}px`;
                }
            }, 0);
            
            e.target._tooltip = tooltip;
        });
        
        btn.addEventListener('mouseleave', (e) => {
            if (e.target._tooltip) {
                e.target._tooltip.remove();
                e.target._tooltip = null;
            }
        });
    });
}

// 既存のPixaAppクラスとの統合
if (typeof PixaApp !== 'undefined') {
    console.log('PixaAppクラスと統合');
    
    // 設定取得メソッドを更新
    PixaApp.prototype.getGenerationSettings = function() {
        const settings = {
            prompt: document.getElementById('prompt').value,
            negative_prompt: document.getElementById('negative-prompt').value,
            model: document.getElementById('model').value,
            steps: parseInt(document.getElementById('steps').value),
            cfg_scale: parseFloat(document.getElementById('cfg-scale').value),
            seed: parseInt(document.getElementById('seed').value),
        };
        
        // モード別の設定を追加
        if (this.currentMode === 'pixel-art') {
            settings.pixel_size = parseInt(document.getElementById('pixel-size').value);
            settings.palette_size = parseInt(document.getElementById('palette-size').value);
            settings.outline = document.getElementById('outline-toggle')?.checked || false;
        } else if (this.currentMode === 'glitch-art') {
            settings.glitch_intensity = parseInt(document.getElementById('glitch-intensity')?.value || 50);
            settings.glitch_pixel_size = parseInt(document.getElementById('glitch-pixel-size')?.value || 4);
        } else if (this.currentMode === 'animation') {
            settings.frame_count = parseInt(document.getElementById('frame-count')?.value || 8);
            settings.fps = parseInt(document.getElementById('fps')?.value || 10);
            settings.animation_type = document.querySelector('.animation-type-card.selected')?.dataset.type || 'idle';
        }
        
        // アスペクト比
        const activeRatio = document.querySelector('.ratio-btn.active');
        if (activeRatio) {
            settings.aspect_ratio = activeRatio.dataset.ratio;
        }
        
        return settings;
    };
    
    // showToastメソッドを追加
    PixaApp.prototype.showToast = showToast;
}

// アニメーションタイプカードの初期化
function initializeAnimationCards() {
    document.querySelectorAll('.animation-type-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // 他のカードの選択を解除
            document.querySelectorAll('.animation-type-card').forEach(c => c.classList.remove('selected'));
            // クリックしたカードを選択
            e.currentTarget.classList.add('selected');
            // アニメーションタイプを表示
            const type = e.currentTarget.dataset.type;
            const label = e.currentTarget.querySelector('span').textContent;
            showToast(`アニメーション: ${label}`, 'info');
        });
    });
}