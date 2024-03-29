import tcod as libtcod
from game_messages import Message
from components.ai import ConfusedMonster

# TODO: Bugfixing; using items doesn't immediately end turn, and no message gets printed?

def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.current_hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message("You are already at full health!", libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message("Your wounds start to feel better!", libtcod.green)})
    
    return results

def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    max_range = kwargs.get('max_range')

    results = []

    target = None
    closest_distance = max_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message("ZAP! ZING! ZOW! {0} takes {1} lightning damage!".format(target.name, damage), libtcod.light_azure)})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('There was no target in range, you fool!', libtcod.light_red)})

    return results
    
def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []
    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message("You cannot target a tile outside your field of view.", libtcod.yellow)})
        return results
    results.append({'consumed': True, 'message': Message("The fireball explodes, burning everything with {0} tiles".format(radius), libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} damage'.format(entity.name, damage), libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))
    return results

def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10, entity)
            entity.ai = confused_ai
            results.append({'consumed': True, 'message': Message("{0} is confused, but it probably won't hurt itself...".format(entity.name), libtcod.light_green)})
            break
    else:
        results.append({'consumed': False, 'message': Message("You must select something that can be confused...", libtcod.yellow)})    

    return results
    
