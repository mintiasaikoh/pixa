"""
最適化設定 - server.pyに追加するコード
"""

# server.pyの先頭付近に追加
import gc
import torch

# グローバル設定に追加
ENABLE_OPTIMIZATIONS = True

# M2 Pro最適化設定
if ENABLE_OPTIMIZATIONS:
    # スレッド数最適化
    torch.set_num_threads(6)  # M2 Proの性能コア数
    
    # MPS最適化
    if torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        # メモリ使用量を75%に制限
        torch.mps.set_per_process_memory_fraction(0.75)

# パイプライン初期化の最適化（initialize_pipeline関数内）
def apply_pipeline_optimizations(pipeline):
    """パイプラインに最適化を適用"""
    if not ENABLE_OPTIMIZATIONS:
        return pipeline
        
    # 1. Attention Slicing（メモリ削減）
    pipeline.enable_attention_slicing(slice_size=1)
    
    # 2. VAE Slicing（大画像でのメモリ削減）
    pipeline.enable_vae_slicing()
    
    # 3. xFormers（利用可能な場合）
    try:
        pipeline.enable_xformers_memory_efficient_attention()
        logger.info("✅ xFormers有効化成功")
    except Exception as e:
        logger.info("⚠️ xFormers未対応")
    
    # 4. Channels Last（メモリレイアウト最適化）
    pipeline.unet = pipeline.unet.to(memory_format=torch.channels_last)
    pipeline.vae = pipeline.vae.to(memory_format=torch.channels_last)
    
    # 5. torch.compile（PyTorch 2.0+）
    if hasattr(torch, 'compile'):
        try:
            pipeline.unet = torch.compile(pipeline.unet, mode="reduce-overhead")
            logger.info("✅ torch.compile有効化成功")
        except:
            logger.info("⚠️ torch.compile未対応")
    
    return pipeline

# 画像生成の最適化（generateエンドポイント内）
def optimized_generate(**kwargs):
    """最適化された画像生成"""
    # 推論モードとautocastを使用
    with torch.inference_mode():
        with torch.autocast(device.type):
            return pipeline(**kwargs)

# メモリクリーンアップ（各生成後）
def cleanup_memory():
    """メモリのクリーンアップ"""
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()
