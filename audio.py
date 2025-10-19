import pygame


class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.current_music = None
        self.volume = 0.7

    def play_music(
        self, filepath="assets/musique/musique_balatro.mp3", loops: int = -1
    ):
        """Jouer une musique en boucle (-1 = infini)."""
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops)
            self.current_music = filepath
        except Exception as e:
            print(f"Erreur lors du chargement de la musique: {e}")

    def stop_music(self):
        """Arrêter la musique."""
        pygame.mixer.music.stop()

    def set_volume(self, volume: float):
        """Régler le volume (0.0 à 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
