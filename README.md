# Narratix
Narratix is a system that transforms narrative explanations into structured visual stories, enabling automated generation of educational animations from text.

## Project Structure

```
NARRATIX/
├── agents/
│   ├── __init__.py
│   └── storyboard_agent.py      # LangChain agent for storyboard generation
├── config/
│   ├── __init__.py
│   └── llm_config.py             # LLM configuration (Ollama/API providers)
├── data/
│   └── storyboard.json           # Generated storyboard (auto-created)
├── input/
│   └── transcript.txt            # Input transcript file (create this)
├── prompts/
│   └── storyboard_prompt.txt     # Prompt template for LLM
├── renderer/
│   ├── __init__.py
│   └── manim_renderer.py         # Manim video renderer
├── scenes/
│   ├── __init__.py
│   └── generated_scene.py        # Generated Manim scene (auto-generated)
├── schemas/
│   └── storyboard_schema.json    # JSON schema for storyboard
├── .env                          # Environment configuration
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Manim

Follow the official Manim installation guide: https://docs.manim.community/en/stable/installation.html

For quick installation:
- **Linux/Mac**: `pip install manim`
- **Windows**: Install dependencies first, then `pip install manim`

### 3. Install LaTeX (Required for Mathematical Equations)

Manim requires LaTeX to render mathematical equations. Choose one:

**Windows:**
- **MiKTeX** (Recommended): https://miktex.org/download
  - Download and install
  - Choose "Install missing packages on-the-fly: Yes"
  - Restart your terminal after installation
  - Verify: `latex --version`

- **TeX Live**: https://tug.org/texlive/windows.html

**Mac:**
```bash
brew install mactex
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install texlive texlive-latex-extra texlive-fonts-extra
```

**Note:** Without LaTeX, equations will fall back to plain text rendering.

### 4. Install Ollama (for local LLM)

Download and install Ollama from https://ollama.ai

Pull the Llama3 model:
```bash
ollama pull llama3
```

### 4. Configure Environment

Edit `.env` file:

```bash
# For local Ollama (default)
USE_API=false
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# For API-based LLMs (OpenAI, Anthropic, Groq)
# USE_API=true
# API_PROVIDER=openai  # or anthropic, groq
# API_KEY=your_api_key_here
```

### 5. Create Input Folder

```bash
mkdir input
```

Then create your transcript in `input/transcript.txt`

## Quick Start Guide

### 1. First Time Setup

```bash
# Clone or create project directory
cd NARRATIX

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install LaTeX (Required!)
# Windows: Download MiKTeX from https://miktex.org/download
# Mac: brew install mactex
# Linux: sudo apt-get install texlive texlive-latex-extra

# Install and start Ollama
# Download from https://ollama.ai
ollama pull llama3
ollama serve

# Create input folder and transcript
mkdir input
# Create input/transcript.txt with your content
```

### 2. Run Your First Video

```bash
# Generate video from input/transcript.txt
python main.py

# Or with higher quality
python main.py --quality h
```

### 3. Check Output

- Storyboard: `data/storyboard.json`
- Generated scene: `scenes/generated_scene.py`
- Video: `media/videos/generated_scene/`

## Usage Examples

```bash
# Use default transcript file (input/transcript.txt)
python main.py

# Use a different transcript file
python main.py --transcript-file my_transcript.txt

# From direct transcript text
python main.py --transcript "Let me explain the Pythagorean theorem..."

# With custom quality (l=low, m=medium, h=high, k=4k)
python main.py --quality h
```

### Advanced Options

```bash
# Generate storyboard only (no video rendering)
python main.py --generate-only

# Use existing storyboard (skip generation)
python main.py --skip-generation --storyboard data/storyboard.json

# Custom output directory
python main.py --output my_videos

# Custom transcript file
python main.py --transcript-file path/to/my_transcript.txt
```

### Using Different LLM Providers

#### 1. Local Ollama (Default)
```bash
# .env
USE_API=false
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

#### 2. OpenAI
```bash
# .env
USE_API=true
API_PROVIDER=openai
API_KEY=sk-...
```

#### 3. Anthropic (Claude)
```bash
# .env
USE_API=true
API_PROVIDER=anthropic
API_KEY=sk-ant-...
```

#### 4. Groq
```bash
# .env
USE_API=true
API_PROVIDER=groq
API_KEY=gsk_...
```

## Example Workflow

1. **Create your transcript** in `input/transcript.txt`:
```
Welcome! Today we'll explore the beauty of the Pythagorean theorem.
The theorem states that in a right triangle, a squared plus b squared equals c squared.
Let me show you why this is true using a visual proof...
```

2. **Generate video**:
```bash
python main.py --quality m
```

3. **Output**:
- `data/storyboard.json` - Generated storyboard
- `scenes/generated_scene.py` - Generated Manim scene code
- `media/videos/` - Rendered video file

## Storyboard JSON Structure

The LLM generates a JSON storyboard with this structure:

```json
{
  "title": "Video Title",
  "description": "Brief description",
  "scenes": [
    {
      "scene_id": 1,
      "duration": 5,
      "narration": "Scene narration text",
      "animation_type": "text",
      "elements": [
        {
          "type": "text",
          "content": "Hello!",
          "position": [0, 0, 0],
          "color": "BLUE",
          "animation": "Write",
          "scale": 1.5
        }
      ]
    }
  ]
}
```

## Supported Element Types

- **text**: Text display
- **equation**: LaTeX mathematical equations
- **circle**: Circle shape
- **square**: Square shape
- **arrow**: Arrow
- **line**: Line
- **axes**: Coordinate axes
- **graph**: Function graph

## Supported Animations

- `Write`: Write text/equation
- `FadeIn`: Fade in element
- `FadeOut`: Fade out element
- `Create`: Create shape
- `Transform`: Transform between elements
- `GrowFromCenter`: Grow from center
- `ShowCreation`: Show creation animation

## Common Issues and Solutions

### "latex not recognized" Error
This is the most common error. You MUST install LaTeX for Manim to work with equations.

**Windows Solution:**
1. Download MiKTeX: https://miktex.org/download
2. Run installer, choose "Install missing packages on-the-fly: Yes"
3. **Important**: Restart PowerShell/Terminal
4. Test: `latex --version`
5. If still not working, add to PATH manually:
   - Search "Environment Variables" in Windows
   - Edit PATH, add: `C:\Program Files\MiKTeX\miktex\bin\x64`

**Quick Test Without LaTeX:**
```bash
# Generate storyboard only (no rendering)
python main.py --generate-only
```

### Virtual Environment Not Activated
```bash
# You should see (venv) in your prompt
# If not:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### LaTeX Not Found Error
**Error**: `'latex' is not recognized as an internal or external command`

**Solution**:
1. Install LaTeX (MiKTeX for Windows, MacTeX for Mac, texlive for Linux)
2. Restart your terminal/PowerShell after installation
3. Verify: `latex --version`
4. If still failing, add LaTeX to your system PATH

**Temporary Workaround**: The code will fall back to plain text for equations if LaTeX is unavailable, but this is not recommended for math-heavy content.

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check the base URL in `.env`
- Verify the model is pulled: `ollama list`

### Manim Rendering Error
- Verify Manim installation: `manim --version`
- Check LaTeX is installed for equation rendering
- Try lower quality first: `python main.py --quality l`

### JSON Parsing Error
- The LLM might not return valid JSON
- Try regenerating with `--generate-only` to inspect output
- Consider using a more capable model (GPT-4, Claude Opus)
- Check `data/storyboard.json` for formatting issues

### Import Errors
- Ensure all `__init__.py` files are present in each folder
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Tips for Better Results

1. **Install LaTeX First**: Mathematical equations won't render properly without it
2. **Clear transcripts**: Write clear, structured transcripts with logical sections
3. **Mathematical content**: Use natural language for math (e.g., "a squared plus b squared")
4. **Scene hints**: Include phrases like "let's visualize this" to trigger animations
5. **Model selection**: GPT-4 or Claude Opus produce better storyboards than smaller models
6. **Test incrementally**: Use `--generate-only` first to check the storyboard before rendering
7. **Start with lower quality**: Use `-ql` (low quality) for faster testing, then `-qh` for final render

## License

MIT License - Feel free to modify and use for your projects!
