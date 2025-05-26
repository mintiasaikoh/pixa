/**
 * Pixa - API通信サービス
 */
class ApiService {
    constructor(baseUrl = 'http://localhost:5001/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * 基本的なHTTP要求
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * 基本画像生成
     */
    async generateImage(params) {
        return this.request('/generate', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * 最適化GIF生成
     */
    async generateOptimizedAnimation(params) {
        return this.request('/generate_optimized_animation', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * 一括最適化GIF生成
     */
    async batchGenerateOptimizedAnimations(params) {
        return this.request('/batch_generate_optimized_animations', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    /**
     * ヘルスチェック
     */
    async healthCheck() {
        return this.request('/health', {
            method: 'GET'
        });
    }

    /**
     * モデル一覧取得
     */
    async getModels() {
        return this.request('/models', {
            method: 'GET'
        });
    }

    /**
     * アニメーションタイプ一覧取得
     */
    async getAnimationTypes() {
        return this.request('/animation_types', {
            method: 'GET'
        });
    }
}

/**
 * グローバルAPIサービスインスタンス
 */
const apiService = new ApiService();

// モジュールエクスポート（ES6 Modules使用時）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiService, apiService };
}
