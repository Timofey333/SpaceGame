up = "up_forward"
down = "down_forward"
left = "left_forward"
right = "right_forward"


def vector(forward) -> tuple[int, int]:
    if forward == up:
        return (0, 1)
    if forward == down:
        return (0, -1)
    if forward == left:
        return (-1, 0)
    if forward == right:
        return (1, 0)

def up_degree(forward) -> int:
    if forward == up:
        return 0
    if forward == down:
        return 180
    if forward == left:
        return 270
    if forward == right:
        return 90