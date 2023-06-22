import pygame, random, os
# Angel Farina

# Ruta absoluta del directorio actual y de carpeta archivos
current_path = os.path.dirname(os.path.abspath(__file__))
files_path = os.path.join(current_path, "files")

# Inicialización de pygame
pygame.init()

# Dimensiones de la pantalla
WIDTH = 800
HEIGHT = 600

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Creación de la pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rainy beers!")

# Ocultar la flecha del mouse
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

# Función para mostrar el puntaje en pantalla
def draw_score(score):
    font = pygame.font.Font(None, 36)
    text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(text, (10, 10))  # Posición puntaje

# Clase personaje
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_right = pygame.image.load(os.path.join(files_path, "player.png")).convert_alpha()
        self.image_right = pygame.transform.scale(self.image_right, (150, 150))
        self.image_left = pygame.transform.flip(self.image_right, True, False)  # Imagen volteada horizontalmente
        self.image = self.image_right  # Imagen inicial
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2  # Centrar jugador horizontalmente
        self.rect.bottom = HEIGHT - 10  # Posición vertical del jugador
        self.collision_rect = pygame.Rect(0, 0, 80, 80)  # Dimensiones del rectángulo de colisión
        self.collision_rect.centerx = self.rect.centerx  # Centrar el rectángulo de colisión horizontalmente
        self.collision_rect.bottom = self.rect.bottom  # Posición vertical del rectángulo de colisión
        self.mouse_direction = None  # Dirección actual del movimiento del ratón

    def update(self):
        # Obtener posición y velocidad actual del ratón
        pos = pygame.mouse.get_pos()
        vel = pygame.mouse.get_rel()[0]

        # Verificar la dirección del movimiento del ratón en el eje x
        if vel < 0:  # Movimiento hacia la derecha
            if self.mouse_direction != "right":
                self.image = self.image_right  # Cambiar a la imagen original
                self.mouse_direction = "right"
        elif vel > 0:  # Movimiento hacia la izquierda
            if self.mouse_direction != "left":
                self.image = self.image_left  # Cambiar a la imagen volteada horizontalmente
                self.mouse_direction = "left"

        self.rect.x = pos[0]
        self.collision_rect.x = pos[0] - self.collision_rect.width // 4  # Posición horizontal del rectángulo de colisión

        # Verificar si el personaje se sale del lado derecho e izquierdo de la pantalla
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0

# Clase cerveza
class Beer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(files_path, "beer.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # Tamaño de la cerveza
        self.rect = self.image.get_rect()
        self.reset_position()
    
    def update(self):
        self.rect.y += self.fall_speed
        if self.rect.y > HEIGHT:
            self.reset_position()
    
    def reset_position(self):
        self.rect.y = random.randint(-HEIGHT, 0)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)  # Posición horizontal aleatoria
        self.fall_speed = random.randint(1, 6)  # Velocidad de caída aleatoria

# Clase para el manejo de sonidos
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.burp_sound = pygame.mixer.Sound(os.path.join(files_path, "barney.mp3"))
        self.burp_sound.set_volume(0.1)
        self.background_music = pygame.mixer.music.load(os.path.join(files_path, "theme.mp3"))
        self.nelson_sound = pygame.mixer.Sound(os.path.join(files_path, "nelson.mp3"))
        self.nelson_sound.set_volume(0.1)
    
    def play_burp_sound(self):
        self.burp_sound.play()
    
    def play_background_music(self):
        pygame.mixer.music.set_volume(0.1)  # Volumen música (0.2 = 20% del volumen máximo)
        pygame.mixer.music.play(-1)  # Reproducir en bucle (-1 indica bucle infinito)

    def play_nelson_sound(self):
        self.nelson_sound.play()

# Clase agua
class Water(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(files_path, "water.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.reset_position()
    
    def update(self):
        self.rect.y += self.fall_speed
        if self.rect.y > HEIGHT:
            self.reset_position()
    
    def reset_position(self):
        self.rect.y = random.randint(-HEIGHT, 0)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.fall_speed = random.randint(1, 6)

# Creación de los sprites
all_sprites = pygame.sprite.Group()
beers = pygame.sprite.Group()
waters = pygame.sprite.Group()

# Creación del personaje
player = Player()
all_sprites.add(player)

# Creación de las cervezas
for i in range(1):
    beer = Beer()
    beer.rect.x = random.randrange(0, WIDTH)
    beer.rect.y = random.randrange(-HEIGHT, 0)
    beers.add(beer)
    all_sprites.add(beer)

# Creación de las aguas
for i in range(1):
    water = Water()
    water.rect.x = random.randrange(0, WIDTH)
    water.rect.y = random.randrange(-HEIGHT, 0)
    waters.add(water)
    all_sprites.add(water)

background = pygame.image.load(os.path.join(files_path, "background.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Creación del SoundManager
sound_manager = SoundManager()

# Función principal del juego
def game_loop():
    # Utilizar la variable last_burp_score global en lugar de declararla localmente
    global last_burp_score, spawn_rate

    # Inicializar variables
    running = True
    score = 0
    last_burp_score = 0
    beer_limit_increment = 0  # Incremento del límite de cervezas que caen
    beer_limit = 3  # Límite inicial de cervezas que caen
    spawn_rate = 60  # Tasa de aparición de nuevas cervezas
    beer_spawn_counter = 0  # Contador para la aparición de nuevas cervezas
    total_waters_caught = 0
   
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        all_sprites.update()  # Actualizar sprites
        
        # Comprobar si el personaje atrapa una cerveza y agua
        beers_caught = pygame.sprite.spritecollide(player, beers, True)
        waters_caught = pygame.sprite.spritecollide(player, waters, True)

        # reinicio todo si se atrapan 3 aguas
        total_waters_caught += len(waters_caught)
        if total_waters_caught >= 3:
            score = 0
            total_waters_caught = 0
            sound_manager.play_nelson_sound()
            beer_limit_increment = 0
            beer_limit = 3

        score += len(beers_caught)

        beer_spawn_counter += 1
        
        # Aumentar la cantidad de cervezas si se cumple la condición
        if score % 50 == 0 and score != 0:
            beer_limit_increment += 1
            beer_limit += beer_limit_increment

        # Aparecer nuevas cervezas si se cumple la condición
        if beer_spawn_counter >= spawn_rate and len(beers) < beer_limit:
            beer = Beer()
            all_sprites.add(beer)
            beers.add(beer)
            beer_spawn_counter = 0

        # Menos botellas de agua que cervezas
        if len(waters) < beer_limit // 3:
                water = Water()
                all_sprites.add(water)
                waters.add(water)
        
        screen.blit(background, (0, 0))  # Dibujar el fondo
        
        # Dibujar los sprites y el puntaje después del fondo
        all_sprites.draw(screen)
        draw_score(score)
       
        # Dibujar el rectángulo de colisión del personaje
        #pygame.draw.rect(screen, (255, 0, 0), player.rect, 2)

        # Reproducir el sonido del eructo cuando el puntaje es múltiplo de 10 y es diferente al último puntaje en el que se reprodujo
        if score % 10 == 0 and score != 0 and score != last_burp_score:
            sound_manager.play_burp_sound()
            last_burp_score = score
            beer_spawn_counter += 5
        
        # Actualizar la pantalla
        pygame.display.flip()
        
        # Limitar la velocidad de fotogramas
        clock.tick(60)

# Iniciar el juego
sound_manager.play_background_music()
game_loop()
