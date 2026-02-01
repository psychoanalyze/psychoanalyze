# Quick Reference: D2 Diagram Skill

## 🎯 Purpose
Generate D2 diagrams for PsychoAnalyze architecture, data flows, and technical concepts.

## 🚀 Quick Start

### Ask GitHub Copilot
```
"Show me a D2 diagram of the data hierarchy"
"Generate an architecture diagram using D2"
"Create a D2 diagram showing the analysis workflow"
```

### View Examples
```bash
# Navigate to diagrams directory
cd .github/skills/diagrams/

# List available diagrams
ls *.d2
# → data-hierarchy.d2
# → module-architecture.d2
# → analysis-workflow.d2
# → psychometric-function.d2

# View a diagram
cat data-hierarchy.d2
```

### Validate Diagrams
```bash
# Validate all diagrams
python3 validate_d2.py *.d2

# Validate specific diagram
python3 validate_d2.py data-hierarchy.d2

# JSON output
python3 validate_d2.py --json *.d2
```

## 📊 Available Diagrams

| Diagram | Size | Description |
|---------|------|-------------|
| `data-hierarchy.d2` | 98 lines | Trials → Points → Blocks → Sessions |
| `module-architecture.d2` | 185 lines | Component relationships |
| `analysis-workflow.d2` | 249 lines | Data processing pipeline |
| `psychometric-function.d2` | 249 lines | Formula ψ(x) components |

## 🎨 Rendering Options

### 1. Online (No Installation)
- Open https://play.d2lang.com/
- Copy `.d2` file contents
- Paste and view
- Export as SVG/PNG

### 2. CLI (Requires d2)
```bash
# Install d2 (see https://d2lang.com)
curl -fsSL https://d2lang.com/install.sh | sh -s --

# Render diagram
d2 data-hierarchy.d2 output.svg

# With theme
d2 --theme=dark data-hierarchy.d2 output.svg

# Batch render
for f in *.d2; do d2 "$f" "${f%.d2}.svg"; done
```

### 3. VS Code
- Install "D2" extension
- Open `.d2` file
- Click preview button

## 🔧 Customization

### Change Colors
```d2
MyShape: {
  style.fill: "#e8f4f8"  # Background
  style.stroke: "#2c5aa0" # Border
}
```

### Change Layout
```d2
direction: down  # or right, left, up
```

### Change Shapes
```d2
MyShape: {
  shape: rectangle  # or oval, cylinder, diamond, hexagon
}
```

## 📚 Learn More

- **Skill Definition**: `.github/skills/d2-diagram.json`
- **Documentation**: `.github/skills/README.md`
- **Technical Details**: `.github/skills/SUMMARY.md`
- **D2 Docs**: https://d2lang.com/tour/intro

## 🐛 Troubleshooting

### Copilot doesn't generate diagrams
- Check that you're in the psychoanalyze repository
- Ensure `.github/skills/d2-diagram.json` exists
- Try rephrasing your request

### D2 syntax error
```bash
# Validate syntax
python3 .github/skills/diagrams/validate_d2.py your-diagram.d2
```

### Can't render diagram
- Use online playground: https://play.d2lang.com/
- Check d2 installation: `d2 --version`
- Verify file path is correct

## ✅ Validation Checklist

- [ ] JSON skill file validates
- [ ] D2 syntax validates
- [ ] Diagram renders correctly
- [ ] Colors are visible
- [ ] Layout is clear
- [ ] Labels are readable

---

*Last updated: 2026-02-01*
