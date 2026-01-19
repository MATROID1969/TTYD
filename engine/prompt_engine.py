# engine/prompt_engine.py

from pathlib import Path
import json


def render_meta_context(meta_path: Path, max_values: int = 30) -> str:
    """
    meta_context.json -> tömör, LLM-barát kivonat.
    A values listákból csak az első max_values elemet tesszük be (hogy ne legyen túl hosszú).
    """
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    lines = []
    lines.append("ADATKÉSZLET META INFORMÁCIÓ")
    lines.append(f"- Dataset: {meta.get('dataset', '')}")
    lines.append(f"- {meta.get('row_semantics', '')}")
    src = meta.get("source")
    if src:
        lines.append(f"- Source: {src}")
    lines.append("")
    lines.append("MEZŐK:")

    for field in meta.get("fields", []):
        name = field.get("name", "")
        ftype = field.get("type", "")
        item_type = field.get("item_type")
        exclude_values = field.get("exclude_values", [])
        values = field.get("values", [])

        line = f'- "{name}" → {ftype}'
        if ftype == "list" and item_type:
            line += f" (item_type={item_type})"
        lines.append(line)

        if values:
            preview = values[:max_values]
            more = "" if len(values) <= max_values else f" … (+{len(values)-max_values})"
            lines.append(f"  values: {', '.join(map(str, preview))}{more}")

        if exclude_values:
            lines.append(f"  exclude_values: {', '.join(map(str, exclude_values))}")

    return "\n".join(lines)


def build_prompt(app_path: str) -> str:
    """
    Univerzális prompt összerakó:
    apps/<app>/prompts/
      - system_prompt.txt (kötelező)
      - meta_context.json (opcionális)
      - recipes.md        (opcionális)
    """
    app_dir = Path(app_path)
    prompts_dir = app_dir / "prompts"

    system_path = prompts_dir / "system_prompt.txt"
    if not system_path.exists():
        raise FileNotFoundError(f"Hiányzik a system_prompt.txt: {system_path}")

    system_prompt = system_path.read_text(encoding="utf-8")

    meta_text = ""
    meta_path = prompts_dir / "meta_context.json"
    if meta_path.exists():
        meta_text = render_meta_context(meta_path)

    recipes_text = ""
    recipes_path = prompts_dir / "recipes.md"
    if recipes_path.exists():
        recipes_text = recipes_path.read_text(encoding="utf-8")

    full = system_prompt.strip()

    if meta_text:
        full += "\n\n" + meta_text.strip()

    if recipes_text:
        full += "\n\n" + recipes_text.strip()

    return full
