"""Draw a screening map from a CSV of zone results."""

import argparse
import csv
import math
from pathlib import Path

from matplotlib import colormaps
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Rectangle


def draw_zone_map(csv_path: str | Path, png_path: str | Path) -> None:
    """Render one square per CSV row and write a PNG."""
    zones = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        columns = {"zone", "x", "y", "score", "abstain"}
        if not columns.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires zone, x, y, score and abstain columns")
        for row in reader:
            try:
                position = int(row["x"]), int(row["y"])
                zone = row["zone"].strip()
                abstain = row["abstain"].strip().lower()
                if not zone or abstain not in {"true", "false", "1", "0"}:
                    raise ValueError("expected a zone label and a true/false or 1/0 abstain value")
                score = None if abstain in {"true", "1"} else float(row["score"])
                if score is not None and not math.isfinite(score):
                    raise ValueError("score must be finite")
                if position in zones:
                    raise ValueError(f"duplicate grid position {position}")
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError(f"CSV line {reader.line_num}: {exc}") from exc
            zones[position] = zone, score

    if not zones:
        raise ValueError("CSV must contain at least one zone")

    figure = Figure(layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    scores = [score for _, score in zones.values() if score is not None]
    colors = ScalarMappable(norm=Normalize(), cmap=colormaps["viridis"])
    colors.set_array(scores)
    if scores:
        colors.autoscale()
        figure.colorbar(colors, ax=axes, label="Screening score")

    has_abstentions = False
    for (x, y), (zone, score) in zones.items():
        if score is None:
            face, hatch, label_color = "white", "///", "black"
            has_abstentions = True
        else:
            face, hatch = colors.to_rgba(score), None
            label_color = "white" if colors.norm(score) < 0.5 else "black"
        axes.add_patch(
            Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor=face, edgecolor="black", hatch=hatch)
        )
        axes.text(
            x, y, zone, ha="center", va="center", color=label_color,
            bbox={"facecolor": face, "edgecolor": "none", "pad": 1},
        )

    axes.autoscale_view()
    axes.set(aspect="equal", xlabel="x", ylabel="y")
    if has_abstentions:
        axes.legend(
            handles=[Patch(facecolor="white", edgecolor="black", hatch="///", label="Abstained")],
            loc="lower center",
            bbox_to_anchor=(0.5, 1),
        )
    figure.savefig(png_path, format="png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw a per-zone screening map.")
    parser.add_argument("csv", type=Path, help="CSV with zone, x, y, score and abstain columns")
    parser.add_argument("--png", type=Path, required=True, help="output PNG path")
    args = parser.parse_args()
    try:
        draw_zone_map(args.csv, args.png)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
