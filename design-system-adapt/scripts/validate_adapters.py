import argparse
import json
import os
from typing import Any, Dict, Iterable


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_figma(path: str) -> None:
    payload = load_json(path)
    require("primitive" in payload, "Figma adapter is missing `primitive`.")
    for token_set in ("semantic/light", "semantic/dark", "pattern/light", "pattern/dark", "component/light", "component/dark"):
        require(token_set in payload, f"Figma adapter is missing `{token_set}`.")
    require("$themes" in payload and len(payload["$themes"]) >= 2, "Figma adapter is missing theme metadata.")
    require("$metadata" in payload and "tokenSetOrder" in payload["$metadata"], "Figma adapter is missing token set order metadata.")


def validate_runtime(path: str) -> None:
    payload = load_json(path)
    require("$themes" in payload, "Runtime adapter is missing `$themes`.")
    for collection in ("semantic", "pattern", "component"):
        require(collection in payload, f"Runtime adapter is missing `{collection}`.")


def validate_ai(path: str) -> None:
    payload = load_json(path)
    require("tokens" in payload, "AI adapter is missing `tokens`.")
    for collection in ("primitive", "semantic", "pattern", "component"):
        require(collection in payload["tokens"], f"AI adapter is missing `tokens.{collection}`.")
    require("componentIndex" in payload, "AI adapter is missing `componentIndex`.")


def validate_exists(paths: Iterable[str]) -> None:
    for path in paths:
        require(os.path.exists(path), f"Expected output does not exist: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated AI, Figma, and runtime adapters.")
    parser.add_argument("--figma", default="adapters/figma/figma_tokens_adaptive.json", help="Path to the generated Figma adapter JSON.")
    parser.add_argument("--ai", default="adapters/ai/ai.tokens.json", help="Path to the generated AI adapter JSON.")
    parser.add_argument("--runtime", default="adapters/runtime/tokens.runtime.json", help="Path to the generated runtime canonical JSON.")
    parser.add_argument("--css", default="adapters/runtime/tokens.css.json", help="Path to the generated CSS runtime JSON.")
    parser.add_argument("--tailwind", default="adapters/runtime/tokens.tailwind.json", help="Path to the generated Tailwind runtime JSON.")
    parser.add_argument("--react", default="adapters/runtime/tokens.react.json", help="Path to the generated React runtime JSON.")
    parser.add_argument("--mobile", default="adapters/runtime/tokens.mobile.json", help="Path to the generated mobile runtime JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_exists((args.figma, args.ai, args.runtime, args.css, args.tailwind, args.react, args.mobile))
    validate_figma(args.figma)
    validate_ai(args.ai)
    validate_runtime(args.runtime)
    load_json(args.css)
    load_json(args.tailwind)
    load_json(args.react)
    load_json(args.mobile)
    print("Validated:")
    print(f"- {args.figma}")
    print(f"- {args.ai}")
    print(f"- {args.runtime}")
    print(f"- {args.css}")
    print(f"- {args.tailwind}")
    print(f"- {args.react}")
    print(f"- {args.mobile}")


if __name__ == "__main__":
    main()
