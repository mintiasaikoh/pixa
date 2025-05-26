# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pixa is an Apple Silicon (M2 Pro) optimized AI pixel art generator built with Stable Diffusion. It's a completely local, privacy-focused application that combines Python Flask backend with vanilla JavaScript frontend to generate pixel art from text prompts in both Japanese and English.

## Architecture

### Backend (`backend/`)
- **Flask server** (`server.py`) serves both API endpoints and static frontend files
- **Unified server design**: Single Flask app handles both backend API and frontend delivery
- **Apple Silicon optimization**: Uses MPS (Metal Performance Shaders) for M2 Pro acceleration
- **Japanese translation system**: Built-in dictionary-based Japanese→English translation for prompts
- **Pixel art post-processing**: Custom pipeline that applies pixelization and color palette restrictions
- **GIF animation generation**: Creates animated pixel art GIFs from static images or frame sequences
- **Creative animations** (`creative_animations.py`): Advanced animation effects with physics-based movements
- **Glitch art generator** (`glitch_art_generator.py`): Procedural glitch art generation without AI

### Frontend (`frontend/`)
- **Vanilla JavaScript architecture** (`app.js`): Single `PixelArtGenerator` class manages entire UI
- **Bootstrap 5 + custom CSS**: Retro pixel art aesthetic with responsive design
- **Real-time parameter controls**: Live sliders for pixel size, palette size, generation steps
- **Clipboard integration**: Advanced clipboard API handling with fallbacks
- **Animation controls**: Frame count, FPS, and animation type selection

### Pygame Desktop Application (`pygame_app.py`)
- **Native desktop interface**: pygame + pygame-gui for cross-platform desktop experience
- **Real-time controls**: Live sliders and parameter adjustment
- **Image display**: Native image rendering with automatic scaling and aspect ratio preservation
- **Keyboard shortcuts**: Ctrl+Enter for generation, Ctrl+S for save
- **Quick prompts**: Predefined prompt buttons for instant art generation
- **Animation preview**: Real-time GIF playback and frame navigation

### Key Technical Patterns

**Stable Diffusion Integration**:
- Pipeline initialization with Apple Silicon-specific optimizations (float32 for MPS)
- Custom prompt enhancement that automatically adds pixel art keywords
- Post-processing pipeline: original image → downscale → color quantization → upscale

**Japanese Language Support**:
- Dictionary-based translation in `translate_japanese_to_english()`
- Automatic language detection using Unicode ranges
- Vocabulary covers animals, characters, locations, adjectives
**Error Handling**:
- MPS-specific fixes for numerical precision issues
- Graceful degradation for clipboard operations
- Comprehensive logging for debugging generation issues

## Animated GIF Generation Feature

### Feature Overview
- **Purpose**: Generate animated GIF files from pixel art
- **Implementation**: Leverages existing Stable Diffusion pipeline to create multiple frames for animation

### Animation Types

#### 1. Basic Animations
- **Idle**: Gentle up-down floating motion
- **Walk**: Side-to-side tilting walk cycle
- **Bounce**: Jumping motion with gravity
- **Glow**: Brightness pulsing effect
- **Rotate**: Simple 360-degree rotation

#### 2. Creative Animations (New!)
- **Glitch Wave**: Digital wave distortion with random glitch effects
- **Explode & Reassemble**: Parts fly apart and smoothly return
- **Pixel Rain**: Pixels fall like rain and reconstruct the image
- **Wave Distortion**: Water-like ripple effects
- **Heartbeat**: Pulsing scale with realistic heartbeat pattern
- **Spiral**: Rotating while scaling in spiral motion
- **Split & Merge**: Image splits into 4 parts that rotate and merge back
- **Electric Shock**: Lightning effects with image distortion
- **Rubber Band**: Elastic stretching and squashing

### Technical Specifications

#### Animation Parameters
- **Frame Count**: 2-16 frames (default: 4)
- **Frame Rate**: 5-30 FPS (default: 10)
- **Loop Settings**: Infinite loop / specified iterations
- **Interpolation**: None / Linear / Easing

#### Generation Methods

1. **Frame-by-Frame Generation**
   - Each frame generated individually via Stable Diffusion
   - Prompts include frame-specific instructions (e.g., "frame 1 of walk cycle")

2. **Base Image Transform**
   - Single base image generated and transformed for animation
   - Transformations: rotation, scaling, position shifts

3. **Sprite Sheet Method**
   - Generate single image with multiple poses
   - Split into frames for animation
#### Backend Implementation (`server.py`)
```python
@app.route('/generate_animation', methods=['POST'])
def generate_animation():
    """
    Generate animated GIF endpoint
    
    Parameters:
    - prompt: Base prompt for generation
    - animation_type: "walk", "idle", "effect", etc.
    - frame_count: Number of frames
    - fps: Frames per second
    - pixel_size: Pixel size for art style
    - palette_size: Color palette size
    """
```

#### Required Dependencies
```txt
imageio==2.31.1  # For GIF generation
imageio-ffmpeg==0.4.8  # Optional video processing
numpy  # For advanced image processing in creative animations
```

### Implementation Phases

#### Phase 1: Basic Implementation (Priority)
- Base image transform method for simple animations
- GIF file save functionality
- Basic UI controls

#### Phase 2: Advanced Features
- Frame-by-frame generation method
- Complex animation types
- Enhanced preview capabilities

#### Phase 3: Optimization
- Generation speed improvements
- Memory usage optimization
- Advanced interpolation algorithms

## Development Commands

### Server Management
```bash
# Start web version (auto-creates venv, installs deps, starts server)
./start_server.sh

# Start pygame desktop version
./start_pygame.sh

# Stop server and cleanup
./stop_server.sh

# Manual server start (for debugging)
cd backend && source ../venv/bin/activate && python server.py
```
### Pygame Desktop Application
```bash
# Start pygame version with automatic backend
./start_pygame.sh

# Manual pygame app start (requires backend running)
source venv/bin/activate && python pygame_app.py
```

### Installation & Dependencies
```bash
# Install dependencies manually
pip install -r backend/requirements.txt

# Create virtual environment
python3 -m venv venv && source venv/bin/activate
```

### Testing & Debugging
```bash
# Check server health
curl http://localhost:5001/health

# Test image generation
curl -X POST http://localhost:5001/generate -H "Content-Type: application/json" -d '{"prompt": "cute cat"}'

# Test animation generation
curl -X POST http://localhost:5001/generate_animation -H "Content-Type: application/json" -d '{"prompt": "walking cat", "animation_type": "walk", "frame_count": 4}'

# Test creative animations
python scripts/test_creative_animations.py

# Check Apple Silicon optimization
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```
## Key Implementation Details

### Apple Silicon Optimizations
- Uses `torch.float32` instead of `float16` to avoid MPS numerical precision errors
- CPU-based random number generation for MPS compatibility
- Attention slicing enabled for memory efficiency

### Server Architecture
- Port 5001 for unified Flask server
- Static file serving integrated into Flask app (`static_folder='../frontend'`)
- CORS enabled for development

### Japanese Translation
The translation system uses a comprehensive dictionary mapping Japanese terms to English equivalents, covering:
- Animals: 猫→cat, 犬→dog, ドラゴン→dragon
- Characters: 騎士→knight, 魔法使い→wizard, 忍者→ninja
- Descriptors: 可愛い→cute, 美しい→beautiful, 強い→strong
- Animation terms: 歩く→walk, 走る→run, ジャンプ→jump

### Pixel Art Processing
1. Generate standard Stable Diffusion image
2. Downscale using nearest neighbor sampling
3. Apply color quantization (configurable palette size)
4. Upscale back to original size maintaining pixel boundaries

### GIF Animation Processing
1. Generate base image or frame sequence
2. Apply pixel art processing to each frame
3. Optimize frame timing and transitions
4. Export as optimized GIF with proper loop settings

### Creative Animation Processing
The `creative_animations.py` module provides advanced animation effects:
- **Physics-based movements**: Gravity, elasticity, and momentum calculations
- **Easing functions**: Smooth acceleration and deceleration
- **Random elements**: Controlled randomness for organic effects
- **NumPy optimizations**: Fast array operations for real-time processing
- **Particle systems**: For effects like pixel rain and explosions
## Constraints & Requirements

- **Apple Silicon required** for optimal performance (M1/M2)
- **Minimum 16GB RAM** recommended for model loading
- **5GB+ storage** for Stable Diffusion model cache
- **Python 3.8+** with virtual environment recommended
- **macOS 12+** for full MPS support

## Configuration

Key configuration happens in `server.py`:
- Model: `runwayml/stable-diffusion-v1-5`
- Device selection: Automatic MPS → CUDA → CPU fallback
- Memory optimizations: attention slicing, xformers (optional)
- Image generation parameters: configurable via API endpoints
- Animation parameters: frame count, FPS, interpolation methods

## Recent Updates (2025-05-26)

### Creative Animations Feature
- Added 9 new creative animation types with physics-based movements
- Created `creative_animations.py` module for advanced effects
- Implemented easing functions and particle systems
- Added test script `scripts/test_creative_animations.py`

### Smart App Launcher
- Created `Pixa.app` with automatic project detection
- Added `create_smart_app.sh` for easy app creation
- Implemented background server management