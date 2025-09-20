import re
import pathlib

import yaml


README_PATH = pathlib.Path('README.md')
AGENT_PATTERN = re.compile(r"\| \[(?P<label>[^\]]+)\]\((?P<path>[^)]+)\) \| (?P<model>[^|]+?) \|")


def extract_agents_from_readme():
    text = README_PATH.read_text()
    agents = {}
    for match in AGENT_PATTERN.finditer(text):
        label = match.group('label').strip()
        path = pathlib.Path(match.group('path').strip())
        model = match.group('model').strip()
        agents[label] = (path, model)
    return agents


def load_frontmatter(path: pathlib.Path) -> dict:
    content = path.read_text()
    segments = content.split('---', 2)
    if len(segments) < 3:
        raise AssertionError(f"{path} is missing YAML frontmatter")
    data = yaml.safe_load(segments[1])
    if not isinstance(data, dict):
        raise AssertionError(f"{path} frontmatter is not a mapping")
    return data


def test_readme_agent_metadata_matches_files():
    agents = extract_agents_from_readme()
    assert agents, "No agents found in README tables"

    for label, (path, model) in agents.items():
        assert path.exists(), f"README references missing agent file: {path}"
        data = load_frontmatter(path)
        assert data.get('name') == label, (
            f"README label '{label}' does not match agent name '{data.get('name')}'"
        )
        assert data.get('model') == model, (
            f"README model for '{label}' is '{model}' but file specifies '{data.get('model')}'"
        )
