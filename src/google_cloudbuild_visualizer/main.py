import time
from argparse import ArgumentParser
from pathlib import Path

import yaml
from graphviz import Digraph
from loguru import logger


def build_graph(data: dict, output: Path, view: bool = False) -> None:
    dot = Digraph(comment="Cloud Build")
    previous_step = "-"
    for idx, step in enumerate(data["steps"]):
        step_id = step.get("id", None)
        if not step_id:
            raise Exception(f"Step {idx} must have an id")
        dot.node(step_id)
        if "waitFor" in step:
            for dependency in step["waitFor"]:
                dot.edge(dependency, step_id)
        elif previous_step is not None:
            dot.edge(previous_step, step_id)
        previous_step = step_id

    dot.render(output, view=view)


def main():
    parser = ArgumentParser("Visualize Cloud Build YAML")
    parser.add_argument("file", help="Cloud Build YAML file")
    DEFAULT_OUTPUT_FILE = Path.home() / ".cloudbuildviz" / f"out-{time.time()}.gv"
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=Path,
        help="Output file",
        default=DEFAULT_OUTPUT_FILE,
    )
    parser.add_argument(
        "-s",
        "--skip-view",
        dest="skip_view",
        help="Skips automatically opening the output file in the default viewer",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    input_file = args.file
    output_file = args.output
    view = not args.skip_view

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logger.error(f"Error creating the output directory {output_file.parent}")
        logger.exception(exc)
        raise SystemExit(1)

    with open(input_file, "r") as stream:
        try:
            logger.info(f"Reading {input_file}")
            data = yaml.safe_load(stream)
            logger.info(f"Visualizing {input_file}")
            build_graph(data, output_file, view)
            logger.info(f"Output written to {output_file}")
        except yaml.YAMLError as exc:
            logger.error(f"Error parsing the YAML file {input_file}")
            logger.exeption(exc)
            raise SystemExit(1)
        except Exception as exc:
            logger.error(f"Error visualizing {input_file}")
            logger.exception(exc)
            raise SystemExit(1)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
