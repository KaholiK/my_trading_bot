# Writer's Coach & Human-Typer Monorepo

A production-ready TypeScript monorepo delivering two ethical writing tools:

1. **Writer's Coach** — Paraphraser + Humanizer (Ethical, Academic-Safe)
2. **Human-Typer** — Chrome MV3 extension that types text with human-like rhythm

## 🏗️ Architecture

````mermaid
graph TB
    subgraph "Apps"
        API[API - NestJS]
        WEB[Web - Next.js]
        EXT[Extension - Chrome MV3]
    end

    subgraph "Packages"
        SHARED[shared - Types & Schemas]
        LLM[llm - Provider Abstraction]
        METRICS[metrics - Readability Analysis]
        UI[ui - React Components]
    end

    subgraph "Infrastructure"
        SUPABASE[(Supabase - DB & Auth)]
    end

    WEB --> API
    EXT --> API
    API --> LLM
    API --> METRICS
    API --> SUPABASE
    WEB --> UI
    LLM --> SHARED
    METRICS --> SHARED
    UI --> SHARED

    style API fill:#e1f5ff
    style WEB fill:#e8f5e9
    style EXT fill:#fff3e0
    style SUPABASE fill:#f3e5f5
</mermaid>

## ✨ Features

### Writer's Coach (Web App)
- **Ethical Paraphrasing**: Improves clarity and natural flow while preserving meaning
- **Citation Lock**: Automatically protects citations from modification
- **Metrics Dashboard**: Real-time readability, sentence variety, passive voice analysis
- **History & Diff**: Token-level comparison between revisions
- **Export**: DOCX and PDF generation
- **Privacy First**: Supabase RLS, no telemetry, export/delete your data

### Human-Typer (Chrome Extension)
- **Natural Typing**: Log-normal delay distribution with micro-pauses
- **Style Presets**: Casual, Fast, Careful, Phone typing patterns
- **Configurable**: Speed, variability, punctuation pauses, error rate
- **Standard Mode**: Works on inputs, textareas, and contentEditable
- **Driver Mode** (optional): Uses Chrome debugger API for stubborn editors
- **Privacy**: Settings only, no data persisted

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0
- **Supabase** account (free tier works)
- **OpenAI** API key (or use mock provider for testing)

### Installation

```bash
# Install pnpm globally if needed
npm install -g pnpm

# Clone and install dependencies
git clone https://github.com/KaholiK/my_trading_bot.git
cd my_trading_bot
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials
````

### Development

```bash
# Run all apps in development mode
pnpm dev

# Or run individually
pnpm --filter api dev      # API server on :3001
pnpm --filter web dev      # Web app on :3000
pnpm --filter extension dev # Extension build

# Type checking
pnpm typecheck

# Linting
pnpm lint

# Run tests
pnpm test

# Seed database
pnpm seed
```

### Building for Production

```bash
# Build all apps
pnpm build

# Start in production mode
pnpm start
```

### Loading the Chrome Extension

1. Build the extension: `pnpm --filter extension build`
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `apps/extension/dist` directory

## 📁 Monorepo Structure

```
/apps
  /api         # NestJS backend (REST API)
  /web         # Next.js frontend (App Router)
  /extension   # Chrome MV3 extension
/packages
  /llm         # LLM provider abstraction (OpenAI, Mock)
  /metrics     # Readability & style metrics with tests
  /ui          # Shared React components
  /shared      # Zod schemas, types, constants
/tooling       # Shared TypeScript & ESLint configs
```

## 🔐 Security & Privacy

- **No Telemetry**: Zero third-party analytics or tracking
- **Supabase RLS**: Users can only access their own data
- **No Secrets in Code**: Environment variables only
- **Data Portability**: Export all your data as JSON
- **Right to Deletion**: Delete all your data with one click
- **Guardrails**: Blocks requests to evade detection tools

## 🛡️ Guardrails (Non-Negotiable)

This tool **refuses** to help with:

- Bypassing AI detectors
- Evading plagiarism detection
- Cheating academic integrity systems
- Making content "undetectable"

If such requests are detected, the API returns:

```json
{
  "error": "Not supported. This app improves clarity and style while preserving meaning and citations."
}
```

## 📊 Metrics Definitions

### Readability

**Flesch Reading Ease** = `206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)`

- Higher score = easier to read
- 90-100: Very easy (5th grade)
- 60-70: Standard (8th-9th grade)
- 0-30: Very difficult (college graduate)

### Sentence Length Variance

Variance of sentence lengths (measured in words per sentence). Higher variance indicates more structural diversity.

### Repetition Ratio

`unique bigrams / total bigrams` (0 to 1)

- Lower ratio = more repetitive phrasing
- Higher ratio = more lexical variety

### Passive Voice %

`(# of passive sentences / total sentences) * 100`
Detected using "be verb + past participle" heuristic.

### Lexical Diversity

`unique tokens / total tokens` (0 to 1)
Type-token ratio measuring vocabulary richness.

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Run tests for specific package
pnpm --filter @writers-coach/metrics test

# Run tests with coverage
pnpm test --coverage
```

## 📝 API Documentation

Once the API server is running, visit:

- **OpenAPI docs**: http://localhost:3001/docs
- **Swagger UI**: http://localhost:3001/api

### Key Endpoints

#### `POST /revise`

Paraphrase and humanize text.

**Request:**

```json
{
  "original_text": "Your text here",
  "controls": {
    "formality": 2,
    "concision": 1,
    "variation": 2,
    "lockCitations": true,
    "keepTermsCsv": "machine learning,neural network"
  }
}
```

**Response:**

```json
{
  "revised_text": "Improved text here",
  "notes": [
    "Varied sentence structure for better flow",
    "Simplified complex clauses for clarity",
    "Preserved technical terminology as requested",
    "Maintained all citations exactly"
  ],
  "summary": "Improved readability while preserving academic tone"
}
```

#### `POST /metrics`

Analyze text readability and style.

**Request:**

```json
{
  "text": "Your text to analyze"
}
```

**Response:**

```json
{
  "readability": 65.4,
  "sentenceLengths": [12, 18, 15, 9],
  "lengthVariance": 12.5,
  "repetitionRatio": 0.83,
  "passivePct": 12.5,
  "lexicalDiversity": 0.67
}
```

## 🎯 Roadmap

### v0.1.0 (Current)

- [x] Monorepo scaffold with pnpm workspaces
- [x] TypeScript configuration and linting
- [x] Git hooks with Husky
- [ ] Supabase schema and migrations
- [ ] Packages: shared, llm, metrics, ui
- [ ] API: NestJS with routes, guardrails, rate limiting
- [ ] Web: Next.js with editor, metrics, history
- [ ] Extension: Standard typing mode
- [ ] CI/CD pipeline
- [ ] Complete documentation

### v0.2.0 (Future)

- [ ] Extension Driver Mode (advanced)
- [ ] Token-level diff with syntax highlighting
- [ ] Per-site extension profiles
- [ ] Advanced metrics (sentiment, tone)
- [ ] Real-time collaboration
- [ ] Mobile responsive improvements

## 🤝 Contributing

This is a production MVP. Contributions welcome via issues and PRs.

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting, missing semi colons, etc.
refactor: code restructuring
test: adding tests
chore: maintenance tasks
```

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with NestJS, Next.js, and TypeScript
- Powered by Supabase and OpenAI
- Inspired by ethical academic writing practices

---

**Status**: 🚧 PR #1 - Monorepo scaffold complete. Building incrementally...
