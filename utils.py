import pygame

def load_image(path, colorkey=None):
    """Charge une image depuis le disque et gère la transparence."""
    try:
        image = pygame.image.load(path)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except pygame.error as message:
        print(f"Impossible de charger l'image : {path}")
        raise SystemExit(message)

def play_sound(path):
    """Joue un son depuis le disque."""
    try:
        sound = pygame.mixer.Sound(path)
        sound.play()
    except pygame.error as message:
        print(f"Impossible de jouer le son : {path}")
        raise SystemExit(message)
