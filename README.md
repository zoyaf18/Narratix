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
├── frontend/                     # React UI (Vite)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
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
├── web/
│   └── server.py                 # FastAPI backend server
├── .env                          # Environment configuration
├── main.py                       # CLI entry point
├── run_local.py                  # One-command UI launcher
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

### 5. Configure Environment

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

### 6. Install Frontend Dependencies (for UI)

```bash
cd frontend
npm install
cd ..
```

## Usage Options

Narratix offers two ways to generate videos:

### Option 1: Web UI (Recommended)

Run the complete web interface with a single command:

```bash
python run_local.py
```

This will:
- Build the React frontend (if needed)
- Start the FastAPI backend at http://localhost:8000
- Serve the UI at http://localhost:8000

**Additional flags:**
- `--no-build`: Skip frontend build (use existing build or run dev server separately)
- `--no-reload`: Start without auto-reload for more stable runs

**Development mode** (with hot module replacement):

Terminal 1 - Start backend:
```bash
uvicorn web.server:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Start frontend dev server:
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 (Vite dev server)

### Option 2: Command Line Interface

Generate videos directly from the command line:

```bash
# Use default transcript file (input/transcript.txt)
python main.py

# Use a different transcript file
python main.py --transcript-file my_transcript.txt

# From direct transcript text
python main.py --transcript "Let me explain the Pythagorean theorem..."

# With custom quality (l=low, m=medium, h=high, k=4k)
python main.py --quality h

# Generate storyboard only (no video rendering)
python main.py --generate-only

# Use existing storyboard (skip generation)
python main.py --skip-generation --storyboard data/storyboard.json
```

## Quick Start Guide

### Web UI Quick Start

```bash
# 1. Ensure all dependencies are installed
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Start Ollama (if using local LLM)
ollama serve

# 3. Launch the UI
python run_local.py

# 4. Open browser to http://localhost:8000
```

### CLI Quick Start

```bash
# 1. Create input folder and transcript
mkdir -p input
echo "Your transcript here..." > input/transcript.txt

# 2. Start Ollama (if using local LLM)
ollama serve

# 3. Generate video
python main.py --quality m

# 4. Check output in media/videos/
```

## Web UI Features

The web interface provides:
- **Transcript Management**: Upload or paste transcripts
- **Storyboard Generation**: Generate and preview storyboards with visual feedback
- **Live Rendering**: Start render jobs with real-time progress updates via WebSocket
- **Output Management**: View, download, and manage generated videos

### API Endpoints

- `POST /transcript` - Upload transcript
- `POST /generate` - Generate storyboard from transcript
- `GET /storyboard` - Retrieve generated storyboard
- `POST /storyboard` - Save edited storyboard
- `POST /render` - Start background render job
- `GET /status/{job_id}` - Check job status
- `WS /ws/{job_id}` - WebSocket for live updates
- `GET /outputs` - List available output files
- `GET /download/{filename}` - Download rendered video

## Using Different LLM Providers

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

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check the base URL in `.env`
- Verify the model is pulled: `ollama list`

### Manim Rendering Error
- Verify Manim installation: `manim --version`
- Check LaTeX is installed for equation rendering
- Try lower quality first: `python main.py --quality l`

### Frontend Build Issues
- Ensure Node.js is installed: `node --version`
- Try clearing node_modules: `cd frontend && rm -rf node_modules && npm install`
- If no package manager available, use Docker fallback:
  ```bash
  docker run --rm -v ${PWD}:/app -w /app/frontend node:18 bash -lc "npm ci && npm run build"
  ```

### Port Already in Use
If port 8000 is already in use, either:
- Stop the other process using port 8000
- Or modify the port in `run_local.py` or when starting uvicorn manually

## Tips for Better Results

1. **Install LaTeX First**: Mathematical equations won't render properly without it
2. **Clear transcripts**: Write clear, structured transcripts with logical sections
3. **Mathematical content**: Use natural language for math (e.g., "a squared plus b squared")
4. **Scene hints**: Include phrases like "let's visualize this" to trigger animations
5. **Model selection**: GPT-4 or Claude Opus produce better storyboards than smaller models
6. **Test incrementally**: Use `--generate-only` first to check the storyboard before rendering
7. **Start with lower quality**: Use `-ql` (low quality) for faster testing, then `-qh` for final render
8. **Web UI for iteration**: Use the web interface to quickly iterate on storyboards and preview before rendering

## Testing

Run tests locally:
```bash
pytest -q
```

A GitHub Actions workflow runs tests automatically on push and pull requests.

## License

MIT License - Feel free to modify and use for your projects!
