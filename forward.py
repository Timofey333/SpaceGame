up = "up_forward"
down = "down_forward"
left = "left_forward"
right = "right_forward"


def opposite(forward) -> str:
    if type(forward) == int:
        forward = form_up_degree(forward)
    elif type(forward) == tuple[int, int]:
        forward = from_vector(forward)
    if forward == up:
        return down
    if forward == down:
        return up
    if forward == left:
        return right
    if forward == right:
        return left


def vector(forward) -> tuple[int, int]:
    if type(forward) == int:
        forward = form_up_degree(forward)
    if type(forward) == tuple[int, int]:
        return forward
    if forward == up:
        return (0, 1)
    if forward == down:
        return (0, -1)
    if forward == left:
        return (-1, 0)
    if forward == right:
        return (1, 0)


def from_vector(forward):
    if forward == (0, 1):
        return up
    if forward == (0, -1):
        return down
    if forward == (-1, 0):
        return left
    if forward == (1, 0):
        return right


def up_degree(forward) -> int:
    if type(forward) == str:
        if forward == up:
            return 0
        if forward == down:
            return 180
        if forward == left:
            return 270
        if forward == right:
            return 90
    elif type(forward) == tuple[int, int]:
        up_degree(from_vector(forward))
    elif type(forward) == int:
        up_degree(form_up_degree(forward))


def form_up_degree(forward):
    if forward == 0:
        return up
    if forward == 180:
        return down
    if forward == 270:
        return left
    if forward == 90:
        return right