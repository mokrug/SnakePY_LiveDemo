import os
import sys
import pygame

# Stelle sicher, dass Pygame im Headless-Modus läuft, wenn nötig
os.environ['SDL_VIDEODRIVER'] = 'dummy'

try:
    import game
    
    # Starte das Spiel
    controller = game.GameController()
    controller.spiel_starten()
except Exception as e:
    print(f"Fehler beim Starten des Spiels: {e}")
    import traceback
    traceback.print_exc()