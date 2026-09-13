FPS = 30


class Player:

    def init(self, speed, pos):
        self._speed: float = speed  # cells/sec
        self._x: float = pos[0]
        self._y: float = pos[1]
        self._direction = (0, 1)

    def get_pos(self):
        return (self._x, self._y)

    def get_next_move(self):
        dx = float(self._direction[0]) * self._speed / FPS
        dy = float(self._direction[1]) * self._speed / FPS
        return (dx, dy)

    def get_next_pos(self):
        dx, dy = self.get_next_move()
        return (dx + self._x, dy + self._y)

    def set_direction(self, direction):
        self._direction = direction

    def get_direction(self):
        return self._direction

    def move(self):
        dx, dy = self.get_next_move()
        print(f"Player moved: ({self._x}, {self._y}) + ({dx}, {dy})")
        self._x += dx
        self._y += dy
