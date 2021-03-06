import pygame
import random
import time
import collections
import math

pygame.init()

#Setting up the colors in "RGB" color-scheme.

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)


#For making the game display size independent, the variables display_width and display_height are calculated and stored.

desktopWidth, desktopHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
display_width = 72 * int(desktopWidth/100)
display_height = 95 * int(desktopHeight/100)

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Retipher")

#Loading the required images/sprites. backg is scaled to the whole display_size so that it may be accomodated in just one blit on the screen.

enemy_face = pygame.image.load('enemy_face.png')
shell_trident = pygame.image.load('shell_trident.png')
gun_shooter = pygame.image.load('gun_shooter.png')
backg = pygame.image.load('backg.jpg')
backg_new = pygame.transform.scale(backg,(display_width,display_height))

clock = pygame.time.Clock()

def showScore(score) :

    """
    Function to print the score (stored in the variable score) in the Top - left corner
    of the screen. The score is incremented
        - if player shot down some enemy target.
    The score is decreamented if any of these happen :-
        1. You get hit by some retaliation bullets shot by enemies.
        2. An enemy passes without being shot down.
    Score is incremented by 10 and decremented by 20.
    """

    font = pygame.font.SysFont("comicsansms", 20, True, True)
    screen_text = font.render("Score : " + str(score), True, black)
    gameDisplay.blit(screen_text, [0, 0])


def message_to_screen(msg, color, vert_displacement=0, size=25, text_font="None", bold="False", italic="False") :

    """
    Function to print a message (msg) on the game-display of colour (color), at a vertical
    distance (vert_displacement) from the x-axis (mid of the game-display) of letter-size (size) using
    the font (text_font) and boolean bold(T/F) and italic(T/F). Note that the text is always centered
    in the horizontal direction.
    """

    font = pygame.font.SysFont(text_font, size, bold, italic)
    screen_text = font.render(msg, True, color)
    text_position = screen_text.get_rect()
    text_position.center = (display_width/2, display_height/2 + vert_displacement)
    gameDisplay.blit(screen_text, text_position)


def gameLoop(title) :


    #The main Game-Loop of game. Writing like this makes it easier to restart the game after Game-over. The
    #loop under "while title" is expected to run only at the start of the Game.

    while title :

        """
        This is the title window of the game which is run just once at the start of the game,
        to ensure this, a bool value "title" is supplied as arguement every time "gameLoop" is
        called, which tells if we need to show the title window (if gameLoop is called for first time)
        or to not show the title window (if the user restarts the game by pressing the "c" after a gameOver)
        """

        gameDisplay.blit(backg_new, (0, 0))

        for event in pygame.event.get() :
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_q :
                    pygame.quit()
                    quit()

                if event.key == pygame.K_c :
                    title = False
                    break

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        message_to_screen("Time to search for bounty", color=red, vert_displacement=-100, size=30, text_font="arial", bold="True")
        message_to_screen("REMEMBER :", color=red, vert_displacement=-60, size=23, text_font="arial")
        message_to_screen("Don't use too many shells, as it may upset the enemy", color=black, vert_displacement=-20, size=17, text_font="timesnewroman")
        message_to_screen("Your score increaments for each succesfull attack on enemy.", color=black, vert_displacement=10, size=17, text_font="timesnewroman")
        message_to_screen("Your score decreaments either when you get hit by enemy or the enemy crosses you. Game Over at score <= -500", color=black, vert_displacement=40, size=17, text_font="timesnewroman")
        message_to_screen("Use Arrow keys for vertical movement and 'Right-arrow key' to fire bullets.", color=black, vert_displacement=70, size=17, text_font="timesnewroman")
        message_to_screen("If you fail, press Q to Quit and C to try again. Press P to Pause and R to restart", color=black, vert_displacement=100, size=17, text_font="timesnewroman")
        message_to_screen("Press C to start the game now !", color=black, vert_displacement=130, size=17, text_font="timesnewroman")

        pygame.display.update()
        clock.tick(15)

    """
    shells => The array maintaining the co-ordinates of bullets fired by you. This would be updated every once and while :-
                1. Elements (a list whose first element is bullet's x-coordinate and second one being y-coordinate) are added whwnever
                new bullets are fired by player (By pressing 'Right arrow' key").
                2. ELements are removed when the bullet either goes off the display or it hits some enemy (in second case, both enemy
                and bullet disappear).
    targets => The array maintaining the co-ordinates of enemies.
    attack => The array maintaining coordinates of the bullets shot by the enemies as retaliation.
    """

    shells = []
    targets = []
    attack = []

    """
    num_targets => The number of targets present at a instant of time on display. These increase when you shoot too much bullets
    "upsetting" the enemies.
    """

    num_targets = 1

    """
    target_size, shell_size, gun_size, step_size => The sizes of enemies, bullets, gun, step that enemy or the player takes in every frame.
    """

    target_size = 30
    shell_size = 20
    gun_size = 20
    step_size = 10

    """
    multiplier => The factor by which enemies would increase if enemies are "upset".
    score => This variable store the current score, thus initialised to 0.
    score_increament, score_decreament => self-explanatory.
    """

    multiplier = 5
    score = 0
    score_increament = 10
    score_decreament = 20
    MAX_SCORE = 10 ** 5

    """
    vert_movement => The variable storing the "step_size" for the vertical movement of targets and "retaliation bullets"
    smooth_degree => The variable storing how accurate the zig-zag the movement of enemies would be.
    random_array_x, random_array_y => Defines smoothness in movement. The number 0f 1's, 0's and -1's are equal in ..._y for unbiased movement. While for ..._x
    the number of -1's are relatively high as resultantly, we have to move to the left.
    min_distance => The variable which would define at what separation between the bullet and target, the target has to attempt dodging.
    FPS => The Frames loaded per second.
    """

    vert_movement = 3
    smooth_degree = 10000
    random_array_y = [random.choice([-1, 1, 0] * 100) for _ in xrange(smooth_degree)]   #equal number of -1, 0, 1
    random_array_x = [random.choice([-1, 1, 0, -1, -1, 0, -1, 0, -1] * 100) for _ in xrange(smooth_degree)]

    min_distance = 100

    # Maximum bullets that can be fired without overcharging the gun
    max_bullets = 8

    # Boolean variable telling if the gun is overcharged or not
    gun_overcharged = 0

    FPS = 15


    #lead_x and lead_y are coordinates of "Shooter". lead_y_change records the direction and step_size of movement in vertical direction (the only allowed
    #direction of movement).
    #gameExit and gameOver stores boolean values for corresponding actions.

    gameExit = False
    gameOver = False

    lead_x = 0
    lead_y = 300

    lead_y_change = 10

    while not gameExit :

        while gameOver :

            """
            This loop runs when you score drops to or below "-500", thus signifying "Game Over".
            By NOT updating the display, or filling it with the background, it is ensured that if someone
            want to check out his score on dying, he can do so right away.
            The game is restarted if 'C' is pressed and quitted if 'Q'/'CROSS' is pressed/clicked.
            """

            message_to_screen("Game Over", color=red, vert_displacement=-20, size=50, text_font="helvetica", bold="True")
            message_to_screen("Press C to continue playing and Q to quit", color=black, vert_displacement=35, size=25, text_font="timesnewroman", italic="True")
            pygame.display.update()

            for event in pygame.event.get() :
                if event.type == pygame.KEYDOWN :
                    if event.key == pygame.K_q :
                        gameExit = True
                        gameOver = False
                        pygame.quit()
                        quit()

                    if event.key == pygame.K_c :
                        gameLoop(False)
                if event.type == pygame.QUIT:
                        gameExit = True
                        gameOver = False

        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                gameExit = True
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN :

                if event.key == pygame.K_q :
                    gameExit = True
                    pygame.quit()
                    quit()

                if event.key == pygame.K_UP :
                    lead_y_change = -10

                elif event.key == pygame.K_DOWN :
                    lead_y_change = 10

                if event.key == pygame.K_RIGHT :
                    lead_x_shell, lead_y_shell = lead_x, lead_y
                    shells.append([lead_x_shell, lead_y_shell])

                elif event.key == pygame.K_p :
                    pauseState = True
                    message_to_screen("WOAH!!, enemy halted attack, take rest", color=red, vert_displacement=-20, size=20, text_font="helvetica",bold="True")
                    message_to_screen("Press C to continue and Q to quit", color=red, vert_displacement=40, size=20, text_font="helvetica", bold="True")


                    #The pause-loop, the game would just keep updating the loop until either 'Q' or 'C' is pressed.

                    while pauseState :
                        pygame.display.update()
                        clock.tick(FPS)

                        for event in pygame.event.get() :
                            if event.type == pygame.KEYDOWN :
                                if event.key == pygame.K_c :
                                    pauseState = False
                                    break

                                elif event.key == pygame.K_q :
                                    pauseState = False
                                    gameExit = True
                                    pygame.quit()
                                    quit()

                #The restart condition - it would call the gameloop with false boolean arguement
                #i.e. without showing the start screen.

                elif event.key == pygame.K_r :
                    gameLoop(False)


        #Movement only in y-direction is allowed.

        lead_y += lead_y_change

        #If the player shoots too many bullets, number of enemies would increase.

        while len(targets) <= num_targets :
            rand_Y = random.randint(2, 15) * target_size
            targets.append([display_width, random.choice([rand_Y, lead_y])])

        total_targets = len(targets)


        #Remove out of screen targets.

        targets = filter(lambda x : x[0] >= 0 and x[1] >= 0 and x[0] <= display_width and x[1] <= display_height, map(lambda x : [x[0] - step_size, x[1]], targets))

        #Decreament the score for every target passing past the player.

        targets_crossed = total_targets - len(targets)
        score -= targets_crossed * score_decreament


        #Remove the shells which are out of the screen.

        shells = filter(lambda x : x[0] <= display_width and 0 <= x[1] <= display_height, map(lambda x : [x[0] + step_size, x[1]], shells))

        gameDisplay.blit(backg_new, (0, 0))

        if len(shells) >= max_bullets :
            message_to_screen("Easy soldier - Bullets don't come for free, Use them judiciously", color=red, vert_displacement=40, size=20, text_font="helvetica", bold="True")
            gun_overcharged = 1
            shells = shells[: max_bullets]
        else :
            gun_overcharged = 0

        for bullet in shells :
            gameDisplay.blit(shell_trident, [bullet[0], bullet[1]])

        for blocks in targets :
            gameDisplay.blit(enemy_face, [blocks[0], blocks[1]])


        #Remove the out of screen retaliating bullets - from the set containing the "fast-x" movement and "random-y" movement.

        attack = filter(lambda x : x[0] >= 0 and x[1] >= 0 and x[0] <= display_width and x[1] <= display_height, map(lambda x : [x[0] - 2 * step_size, x[1] - vert_movement * random.choice(random_array_y)], attack))

        for retal in attack :
            gameDisplay.blit(shell_trident, [retal[0] , retal[1]])

        """
        The 'Dodging function' - AI :-
        If the distance between some target and some 'attacking' bullet is less than the min_distance (defined earlier),
        the target is moved in x-direction opposite to that of as usual (so as to nullify the movement caused in line 319,
        due to this it seems that enemy hasn't moved in x-direction at all and is just concentrating on dodging the bullet
        by halting as opposed to moving towards it) and for y-direction (so as to dodge), different logic is used.
        The block would move up or down (i.e. math.copysign(...) would give negative or positive respectively) if the bullet
        is below or above the target respaectively. Also, to have 'selective'ness in dodging, some random elements [-1, 1] are
        added to the array with 'copysign()' value. To increase the dodging capability with increase/decrease in score, a decreasing
        ratio decides number of random elements added.
        """

        for blocks in targets :
            for bullet in shells :
                if (blocks[0] - bullet[0]) ** 2 + (blocks[1] - bullet[1]) ** 2 < min_distance ** 2 :
                    blocks[0] -= 1
                    blocks[1] += 10 * random.choice([int(math.copysign(1, blocks[1] - bullet[1]))] + [-1, 1] * (MAX_SCORE / abs(score + 1)))

            # If the number of retaliating bullets are less than nuber of targets
            # or both the enemy and the player are at the same level, then shoot some retaliating bullets
            if len(attack) <= len(targets) or blocks[1] == lead_y:
                attack.append([blocks[0], blocks[1]])

        #If there is a collision between the targets and attack-bullets, increament the score.

        for bullet in shells :
            for blocks in targets :
                if blocks[0] <= bullet[0] <= blocks[0] + target_size and blocks[1] <= bullet[1] <= blocks[1] + target_size :
                    if not gun_overcharged :
                        del targets[targets.index(blocks)]
                    bullet[0] = display_width
                    score += score_increament

        #If there is a collision between the player and the retaliating bullets, decreament the score.

        for retal in attack :
            if lead_x <= retal[0] <= lead_x + shell_size :
                if lead_y <= retal[1] <= lead_y + shell_size :
                    del attack[attack.index(retal)]
                    score -= score_decreament

        #Game Over => if score drops till or below to -500.

        if score <= -500 :
            gameOver = True

        gameDisplay.blit(gun_shooter, [lead_x, lead_y])
        showScore(score)

        pygame.display.update()
        clock.tick(FPS)


gameLoop(True)

pygame.quit()
quit()
