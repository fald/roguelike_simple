import tcod as libtcod
from math import ceil

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError("Cannot have such a large menu. Less is more, omae.")
    
    # Calculate total height for header after auto-wrap, with one line per option.
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    # Create off-screen console to represent menu window.
    window = libtcod.console_new(width, height)

    # Print header, auto-wrapped.
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # Print all options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '({0}) {1}'.format(chr(letter_index), option_text)
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
    
    # Blit contents of window onto root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    # Show menu with each inventory item as an option
    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 8, 
                            libtcod.BKGND_NONE, libtcod.CENTER, "THIS PLACE REEKS")
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4,
                            libtcod.BKGND_NONE, libtcod.CENTER, "Shamefully by Firas")
    
    menu(con, '', ['Play New Game', 'Continue Last Game', 'Quit'], 24, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
    
def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    # Looks gross
    old_hp = player.fighter.max_hp
    new_hp = ceil(old_hp * 1.2)
    old_power = player.fighter.old_power
    new_power = ceil(old_power * 1.2)
    old_defense = player.fighter.defense
    new_defense = ceil(old_defense * 1.2)
    options = ['CON: +20% HP ({0}->{1})'.format(old_hp, new_hp),
                'STR: +20% ATK ({0}->{1})'.format(old_power, new_power),
                'AGI: +20% DEF ({0}->{1})'.format(old_defense, new_defense)]

    menu(con, header, options, menu_width, screen_width, screen_height)

# Woops, no options, kind of pointless
# def character_screen_menu(con, header, player, width, screen_width, screen_height):
#     stats = [
#         'Name: {0}'.format(player.name),
#         'Level: {0}'.format(player.level.curr_level),
#         'XP: {0}/{1}'.format(player.level.curr_xp, player.level.experience_to_next_level),
#         'HP {0}/{1}'.format(player.fighter.current_hp, player.fighter.max_hp),
#         'Power: {0}'.format(player.fighter.power),
#         'Defense: {0}'.format(player.fighter.defense)
#     ]

#     menu(con, header, stats, width, screen_width, screen_height)

def character_screen_menu(player, character_screen_width, character_screen_height, screen_width, screen_height):
    display = [
        'Character Information',
        'Name: {0}'.format(player.name),
        'Level: {0}'.format(player.level.curr_level),
        'XP: {0}/{1}'.format(player.level.curr_xp, player.level.experience_to_next_level),
        'HP {0}/{1}'.format(player.fighter.current_hp, player.fighter.max_hp),
        'Power: {0}'.format(player.fighter.power),
        'Defense: {0}'.format(player.fighter.defense)
    ]
    window = libtcod.console_new(character_screen_width, character_screen_height)
    libtcod.console_set_default_foreground(window, libtcod.white)

    for i in range(len(display)):
        libtcod.console_print_rect_ex(
            window, 0, i, character_screen_width, character_screen_height,
            libtcod.BKGND_NONE, libtcod.LEFT, display[i]
        )
    
    x = screen_width // 2
    y = screen_height // 2
    libtcod.console_blit(window, 0, 0, character_screen_width, character_screen_height, 0, x, y, 1.0, 0.7)
