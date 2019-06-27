import tcod as libtcod
from game_messages import Message

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
        results.append({'consumed': True, 'target': target, 'message': Message("ZAP! ZING! ZOW! {0} takes {1} lightning damage!".format(target, damage), libtcod.light_azure)})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False, 'target': None, 'message': Message('There was no target in range, you fool!', libtcod.light_red)})

    return results
    