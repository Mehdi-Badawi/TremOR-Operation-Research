import subprocess
import sys

from matplotlib.figure import Figure

from tremor_screen.zone_map import draw_zone_map


def test_cli_writes_png(tmp_path):
    source = tmp_path / "zones.csv"
    source.write_text("zone,x,y,score,abstain\nA,0,0,0.4,false\n", encoding="utf-8")
    output = tmp_path / "zones.png"

    subprocess.run(
        [sys.executable, "-m", "tremor_screen.zone_map", str(source), "--png", str(output)],
        check=True,
    )

    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_abstained_zones_are_hatched_and_excluded_from_scale(tmp_path, monkeypatch):
    source = tmp_path / "zones.csv"
    source.write_text(
        "zone,x,y,score,abstain\nA,0,0,0.2,0\nB,1,0,,TRUE\n"
        "C,0,1,0.8,false\nD,1,1,100,1\n",
        encoding="utf-8",
    )
    figures = []
    monkeypatch.setattr(Figure, "savefig", lambda figure, *args, **kwargs: figures.append(figure))

    draw_zone_map(source, tmp_path / "zones.png")

    grid, scale = figures[0].axes
    assert [bool(patch.get_hatch()) for patch in grid.patches] == [False, True, False, True]
    assert grid.patches[0].get_facecolor() != grid.patches[2].get_facecolor()
    assert scale.get_ylim() == (0.2, 0.8)
