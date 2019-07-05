import tcod as libtcod
from input_handlers import handle_keys, handle_mouse
from entity import Entity, get_blocking_entities_at_location
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.ai import BasicMonster
from components.fighter import Fighter
from components.inventory import Inventory
from components.item import Item
from death_functions import kill_monster, kill_player
from game_messages import MessageLog, Message
from menus import inventory_menu
from loader_functions.initialize_new_game import get_constants

# TODO: Bugs with using item (no message)
# TODO: Bugs with dropping item (doesn't show on map)

def main():
    constants = get_constants()

    player_fighter_component = Fighter(30, 3, 3)
    player_inventory_component = Inventory(26)
    player = Entity(0, 0, '@', libtcod.white, "Player", blocks=True, render_order=RenderOrder.ACTOR, fighter=player_fighter_component, inventory=player_inventory_component)

    entities = [player]

    libtcod.console_set_custom_font('./Assets/arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities, constants['max_monsters_per_room'], constants['max_items_per_room'])

    # Apart from special circumstances (ie using a torch or whatever),
    # don't need to update fov each turn, just when moving.
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYER_TURN
    # Will be used to return to previous state in case of, for example, opening menu
    previous_game_state = game_state

    targeting_item = None

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])

        render_all(con, panel, message_log, mouse, entities, player, game_map, fov_map, fov_recompute, constants['screen_width'], constants['screen_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], constants['colors'], game_state)
        fov_recompute = False

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        open_inventory = action.get('open_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')
        player_turn_results = []

        if open_inventory:
            previous_game_state = game_state
            game_state = GameStates.MENU_SCREEN
        
        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY
        
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.MENU_SCREEN:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                player_turn_results.extend(player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                target_x=target_x, target_y=target_y))
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if game_state == GameStates.PLAYER_TURN:
            # TODO: Put in a handler for results, separate function >_>
            if move:
                # if move and game_state == GameStates.PLAYER_TURN:
                dx, dy = move
                destination_x = player.x + dx
                destination_y = player.y + dy

                if not game_map.is_blocked(destination_x, destination_y):
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                    if target:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    else:
                        player.move(dx, dy)
                        fov_recompute = True
                    game_state = GameStates.ENEMY_TURN
            
                # for result in player_turn_results:
                #     message = result.get('message')
                #     dead_entity = result.get('dead')

                #     if message:
                #         message_log.add_message(message)
                #     if dead_entity:
                #         if dead_entity == player:
                #             message, game_state = kill_player(dead_entity)
                #         else:
                #             message = kill_monster(dead_entity)
                #         message_log.add_message(message)
            # Whoa, a different action!
            elif pickup:
                for entity in entities:
                    if entity.item and entity.x == player.x and entity.y == player.y:
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)
                        game_state = GameStates.ENEMY_TURN
                        # Only one item pickup at a time, remove for multi
                        break
                else:
                    message_log.add_message(Message("There is nothing here to pick up...", libtcod.yellow))

        if exit:
            if game_state in [GameStates.MENU_SCREEN, GameStates.DROP_INVENTORY]:
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # TODO: Quick reset when player dies.
        # if game_state == GameStates.PLAYER_DEAD:
        #     pass

        for result in player_turn_results:
            # Taking this out of the PLAYER_TURN if-block so it'll take care of things like targeting, too...
            message = result.get('message')
            dead_entity = result.get('dead')
            item_added = result.get('item_added')
            item_used = result.get('consumed')
            item_dropped = result.get('item_dropped')
            targeting = result.get('targeting')
            targeting_cancelled = result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                message_log.add_message(message)
            if item_added:
                entities.remove(item_added)
                # Should probably end turn if picked up an item
                game_state = GameStates.ENEMY_TURN
            if item_used:
                game_state = GameStates.ENEMY_TURN
            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN
            if targeting:
                # So cancelling targeting won't revert to inventory window
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)
            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message("Targeting cancelled"))

       # Enemy Turn (useful comment #1)
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    entity_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    for result in entity_turn_results:
                        message = result.get('message')
                        dead_entity = result.get('dead')
                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)
                            message_log.add_message(message)
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else: # for-else for when the break in the for is triggered
                game_state = GameStates.PLAYER_TURN

if __name__ == "__main__":
    main()
