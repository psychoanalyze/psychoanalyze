import psychoanalyze as pa


def load(points):
    points["Reference Charge (nC)"] = points.index.get_level_values(
        "Amp2"
    ) * points.index.get_level_values("Width2")
    points = points[points["Reference Charge (nC)"] == 0]
    points["Dimension"] = pa.blocks.dimension(points)
    return points
