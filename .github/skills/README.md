# GitHub Copilot Skills

This directory contains custom GitHub Copilot skills for the PsychoAnalyze project.

## Available Skills

### D2 Diagram Generation (`d2-diagram.json`)

Generate D2 (declarative diagramming language) diagrams that illustrate various aspects of the PsychoAnalyze project architecture and workflows.

#### Capabilities

- **Data Hierarchy**: Visual representation of the core data model (Trials → Points → Blocks → Sessions)
- **Module Architecture**: Component relationships and module interactions
- **Analysis Workflow**: Data flow through analysis pipelines
- **Psychometric Function**: Formula components and computation flow

#### Usage

Ask GitHub Copilot to generate diagrams using natural language:

```
"Show me a D2 diagram of the data hierarchy"
"Generate an architecture diagram using D2"
"Create a D2 diagram showing the analysis workflow"
"Draw a diagram of the psychometric function components"
```

#### Rendering D2 Diagrams

The skill outputs D2 source code, which can be rendered in several ways:

1. **Online Playground**: Copy the D2 code to https://play.d2lang.com/
2. **Local CLI**: Install d2 from https://d2lang.com/ and run:
   ```bash
   echo '<d2-code>' | d2 - output.svg
   ```
3. **VS Code Extension**: Install the D2 extension for inline preview

#### Example Output

```d2
direction: down

Trials: {
  shape: cylinder
  label: "Trials\n(Intensity, Result)"
}

Points: {
  shape: cylinder
  label: "Points\n(Hit Rate = Hits / n trials)"
}

Blocks: {
  shape: cylinder
  label: "Blocks\n(threshold + slope from logistic)"
}

Sessions: {
  shape: cylinder
  label: "Sessions/Subjects\n(Longitudinal groupings)"
}

Trials -> Points: "aggregate\nby intensity"
Points -> Blocks: "fit\nlogistic"
Blocks -> Sessions: "group\nby time/subject"
```

## About D2

D2 is a modern diagram scripting language that:
- Uses declarative syntax (describe what, not how)
- Is version-control friendly (plain text)
- Supports multiple layout engines (dagre, elk, etc.)
- Generates high-quality SVG/PNG output
- Integrates with documentation workflows

Learn more at [d2lang.com](https://d2lang.com/)

## Adding New Skills

To add a new skill:

1. Create a JSON file in this directory following the schema pattern
2. Include clear `description`, `instructions`, and `examples`
3. Document usage in this README
4. Test with GitHub Copilot

## References

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [D2 Language Documentation](https://d2lang.com/tour/intro)
- [PsychoAnalyze Copilot Instructions](../copilot-instructions.md)
