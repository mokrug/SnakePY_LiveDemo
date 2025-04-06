import pygame
import random
from typing import List, Tuple
import json
import os

class Snake:
    def __init__(self):
        # Startposition der Schlange in der Mitte
        self.korper = [(300, 300)]  # Liste von (x,y) Koordinaten
        self.richtung = (20, 0)  # Start nach rechts
        self.kopf_position = self.korper[0]
        self.block_size = 20

    def bewegen(self):
        """Bewegt die Schlange in die aktuelle Richtung"""
        neue_position = (
            self.kopf_position[0] + self.richtung[0],
            self.kopf_position[1] + self.richtung[1]
        )
        self.korper.insert(0, neue_position)
        self.kopf_position = neue_position
        self.korper.pop()

    def wachsen(self):
        """Fügt einen neuen Block am Ende der Schlange hinzu"""
        # Dupliziere das letzte Segment
        self.korper.append(self.korper[-1])

    def zeichne(self, screen):
        """Zeichnet die Schlange auf den Bildschirm"""
        for segment in self.korper:
            pygame.draw.rect(screen, (0, 255, 0),
                           (segment[0], segment[1], self.block_size, self.block_size))

    def prufe_kollision(self) -> bool:
        """Prüft Kollision mit Wänden und sich selbst"""
        # Wandkollision
        if (self.kopf_position[0] < 0 or 
            self.kopf_position[0] >= 600 or
            self.kopf_position[1] < 0 or 
            self.kopf_position[1] >= 600):
            return True
            
        # Selbstkollision - prüfe gegen jeden Körperteil außer dem Kopf
        for segment in self.korper[1:]:
            if self.kopf_position == segment:
                return True
        return False

class Apple:
    def __init__(self):
        self.block_size = 20
        self.position = self.neu_generieren()

    def neu_generieren(self) -> Tuple[int, int]:
        """Generiert eine neue zufällige Position für den Apfel"""
        # Begrenzen der möglichen Positionen auf das Spielfeld
        max_x = (600 - self.block_size) // self.block_size
        max_y = (600 - self.block_size) // self.block_size
        x = random.randint(0, max_x) * self.block_size
        y = random.randint(0, max_y) * self.block_size
        return (x, y)

    def zeichne(self, screen):
        """Zeichnet den Apfel auf den Bildschirm"""
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.position[0], self.position[1], self.block_size, self.block_size))

class GameController:
    def __init__(self):
        # Lade Konfiguration
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        pygame.init()
        
        # Setze Position des Hauptfensters
        os.environ['SDL_VIDEO_WINDOW_POS'] = "30,30"
        
        # Erstelle Hauptfenster
        self.screen = pygame.display.set_mode(
            (self.config['main_window']['width'],
             self.config['main_window']['height'])
        )
        pygame.display.set_caption("Snake - by Moritz Krug")
        
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        """Setzt alle Spielwerte zurück"""
        self.score = 0
        self.laufzeit = 0
        self.is_game_over = False
        self.is_paused = False
        self.snake = Snake()
        self.apple = Apple()
        # Stelle sicher, dass der Apfel nicht auf der Schlange spawnt
        while self.apple.position in self.snake.korper:
            self.apple.position = self.apple.neu_generieren()

    def update(self):
        """Aktualisiert den Spielzustand"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.is_game_over:
                        self.reset_game()
                    elif event.key == pygame.K_p:
                        self.is_paused = not self.is_paused
                    elif not self.is_paused and not self.is_game_over:
                        self._handle_input(event.key)

            if not self.is_game_over and not self.is_paused:
                # Prüfe Apfel-Kollision mit dem Kopf
                if self.snake.kopf_position == self.apple.position:
                    self.score += 1
                    self.snake.wachsen()
                    
                    # Generiere neue Position für den Apfel
                    neue_position = self.apple.neu_generieren()
                    # Stelle sicher, dass der Apfel nicht auf der Schlange spawnt
                    max_versuche = 100
                    versuche = 0
                    while neue_position in self.snake.korper and versuche < max_versuche:
                        neue_position = self.apple.neu_generieren()
                        versuche += 1
                    self.apple.position = neue_position

                self.snake.bewegen()
                self.is_game_over = self.snake.prufe_kollision()

            return True
            
        except Exception as e:
            print(f"Fehler im Update: {str(e)}")
            return True

    def render(self):
        """Zeichnet das Spiel auf den Bildschirm"""
        try:
            # Hintergrund zeichnen
            self.screen.fill((0, 0, 0))
            
            # Schlange zeichnen
            self.snake.zeichne(self.screen)
            
            # Apfel zeichnen
            self.apple.zeichne(self.screen)
            
            # Spielinformationen zeichnen
            self._draw_game_info()
            
            # Bildschirm aktualisieren
            pygame.display.flip()
            
            # FPS begrenzen
            self.clock.tick(self.config['main_window']['fps'])
            
        except Exception as e:
            print(f"Fehler beim Rendern: {str(e)}")
    
    def _draw_game_info(self):
        """Zeichnet Spielinformationen wie Punktestand"""
        # Schriftart für Text
        font = pygame.font.SysFont('Arial', 20)
        
        # Punktestand anzeigen
        score_text = font.render(f'Punkte: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Game Over Nachricht
        if self.is_game_over:
            game_over_font = pygame.font.SysFont('Arial', 40)
            game_over_text = game_over_font.render('Game Over! Drücke R zum Neustarten', True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/2))
            self.screen.blit(game_over_text, text_rect)
        
        # Pause Nachricht
        if self.is_paused:
            pause_font = pygame.font.SysFont('Arial', 40)
            pause_text = pause_font.render('Pause', True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen.get_width()/2, self.screen.get_height()/2))
            self.screen.blit(pause_text, text_rect)

    def spiel_starten(self):
        """Hauptspielschleife"""
        running = True
        try:
            while running:
                running = self.update()
                self.render()
        except Exception as e:
            print(f"Kritischer Fehler: {str(e)}")
        finally:
            pygame.quit()

    def _handle_input(self, key):
        """Verarbeitet Tastatureingaben"""
        if key == pygame.K_UP and self.snake.richtung != (0, 20):
            self.snake.richtung = (0, -20)
        elif key == pygame.K_DOWN and self.snake.richtung != (0, -20):
            self.snake.richtung = (0, 20)
        elif key == pygame.K_LEFT and self.snake.richtung != (20, 0):
            self.snake.richtung = (-20, 0)
        elif key == pygame.K_RIGHT and self.snake.richtung != (-20, 0):
            self.snake.richtung = (20, 0)

# Spiel starten
if __name__ == "__main__":
    game = GameController()
    game.spiel_starten()