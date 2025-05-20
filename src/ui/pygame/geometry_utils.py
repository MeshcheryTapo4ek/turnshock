# relative path: src/ui/pygame/geometry_utils.py
def cell_center(pos, cell: int, left: int, top: int) -> tuple[int, int]:
    return (
        left + pos.x * cell + cell // 2,
        top + pos.y * cell + cell // 2,
    )
