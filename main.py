import game

if __name__ == "__main__":
    controller = game.GameController()
    running = True
    while running:
        running = controller.update()
        controller.render()