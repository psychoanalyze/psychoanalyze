import psychoanalyze as pa


def load(points):
    points["Reference Charge (nC)"] = points.index.get_level_values(
        "Amp2"
    ) * points.index.get_level_values("Width2")
    detection_points = points[points["Reference Charge (nC)"] == 0]
    detection_points["Dimension"] = pa.blocks.dimensions(detection_points)
    return detection_points
