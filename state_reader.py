from settings import extraction_settings, singlext_settings, seqext_settings
from interface import *
from game_entities import *
import analysis_examples as analysis #(includes analysis.py analyzers)
import sys
import math
import time
import atexit

zPlayer        = read_int(player_pointer, rel=True)
zBulletManager = read_int(bullet_manager_pointer, rel=True)
zEnemyManager  = read_int(enemy_manager_pointer, rel=True)
zItemManager   = read_int(item_manager_pointer, rel=True)
zLaserManager  = read_int(laser_manager_pointer, rel=True)
zSpellCard     = read_int(spellcard_pointer, rel=True)
zGui           = read_int(gui_pointer, rel=True)
ddcSeijaAnm    = read_int(seija_anm_pointer, rel=True)

#For quick access
analyzer, requires_bullets, requires_enemies, requires_items, requires_lasers, requires_screenshots = extraction_settings.values()
exact = seqext_settings['exact']
need_active = seqext_settings['need_active']
        
def tabulate(x, min_size=10):
    x_str = str(x)
    to_append = min_size - len(x_str)
    return x_str + " "*to_append

def extract_bullets():
    bullets = []
    current_bullet_list = read_zList(zBulletManager + zBulletManager_list)
        
    while current_bullet_list["next"]:
        current_bullet_list = read_zList(current_bullet_list["next"]) 
            
        zBullet        = current_bullet_list["entry"]
        bullet_x       = read_float(zBullet + zBullet_pos)
        bullet_y       = read_float(zBullet + zBullet_pos + 0x4)
        bullet_vel_x   = read_float(zBullet + zBullet_velocity)
        bullet_vel_y   = read_float(zBullet + zBullet_velocity + 0x4)
        bullet_speed   = read_float(zBullet + zBullet_speed)
        bullet_angle   = read_float(zBullet + zBullet_angle)
        bullet_scale   = read_float(zBullet + zBullet_scale)
        bullet_radius  = read_float(zBullet + zBullet_hitbox_radius)
        bullet_delay   = read_int(zBullet + zBullet_ex_delay_timer)
        bullet_iframes = read_int(zBullet + zBullet_iframes)
        bullet_type    = read_int(zBullet + zBullet_type, 2)
        bullet_color   = read_int(zBullet + zBullet_color, 2)
                        
        bullets.append(Bullet(
            position      = (bullet_x, bullet_y), 
            velocity      = (bullet_vel_x, bullet_vel_y), 
            speed         = bullet_speed,
            angle         = bullet_angle,
            scale         = bullet_scale,
            hitbox_radius = bullet_radius,
            show_delay    = bullet_delay,
            iframes       = bullet_iframes,
            bullet_type   = bullet_type,
            color         = bullet_color,
        ))
        
    return bullets
    
def extract_enemies():
    enemies = []
    current_enemy_list = {"entry": 0, "next": read_int(zEnemyManager + zEnemyManager_list)}
        
    while current_enemy_list["next"]:
        current_enemy_list = read_zList(current_enemy_list["next"]) 
        
        zEnemy = current_enemy_list["entry"]
        zEnemyFlags = read_int(zEnemy + zEnemy_flags)
        
        if zEnemyFlags & zEnemyFlags_is_real != 0: 
            continue
            
        enemy_x            = read_float(zEnemy + zEnemy_pos)
        enemy_y            = read_float(zEnemy + zEnemy_pos + 0x4)
        enemy_hurtbox_x    = read_float(zEnemy + zEnemy_hurtbox)
        enemy_hurtbox_y    = read_float(zEnemy + zEnemy_hurtbox + 0x4)
        enemy_hitbox_x     = read_float(zEnemy + zEnemy_hitbox)
        enemy_hitbox_y     = read_float(zEnemy + zEnemy_hitbox + 0x4)
        enemy_is_boss      = zEnemyFlags & zEnemyFlags_is_boss != 0
        enemy_subboss_id   = read_int(zEnemy + zEnemy_subboss_id)
        enemy_rotation     = read_float(zEnemy + zEnemy_rotation)
        enemy_score_reward = read_int(zEnemy + zEnemy_score_reward)
        enemy_hp           = read_int(zEnemy + zEnemy_hp)
        enemy_hp_max       = read_int(zEnemy + zEnemy_hp_max)
        enemy_iframes      = read_int(zEnemy + zEnemy_iframes)
        
        enemies.append(Enemy(
            position     = (enemy_x, enemy_y), 
            hurtbox      = (enemy_hurtbox_x, enemy_hurtbox_y), 
            hitbox       = (enemy_hitbox_x, enemy_hitbox_y), 
            is_boss      = enemy_is_boss,
            subboss_id   = enemy_subboss_id,
            rotation     = enemy_rotation,
            score_reward = enemy_score_reward,
            hp           = enemy_hp, 
            hp_max       = enemy_hp_max,
            iframes      = enemy_iframes,
        ))
    
    return enemies
    
def extract_items():
    items = []
    current_item = zItemManager + zItemManager_array
    
    while current_item < zItemManager + zItemManager_array_len:
        current_item += zItem_len
        
        if read_int(current_item + zItem_state) == 0:
            continue
            
        item_type = get_item_type(read_int(current_item + zItem_type))
        
        if not item_type:
            continue
        
        item_x     = read_float(current_item + zItem_pos)
        item_y     = read_float(current_item + zItem_pos + 0x4)
        item_vel_x = read_float(current_item + zItem_vel)
        item_vel_y = read_float(current_item + zItem_vel + 0x4)
        
        items.append(Item(
            item_type = item_type, 
            position  = (item_x, item_y), 
            velocity  = (item_vel_x, item_vel_y),
        ))
    
    return items
    
def extract_lasers():
    lasers = []
    current_laser_ptr = read_int(zLaserManager + zLaserManager_list) #pointer to head laser 
    
    while read_int(current_laser_ptr + zLaserBaseClass_next): #excludes last (dummy) laser
        laser_state    = read_int(current_laser_ptr + zLaserBaseClass_state)
        laser_type     = read_int(current_laser_ptr + zLaserBaseClass_type)
        laser_timer    = read_int(current_laser_ptr + zLaserBaseClass_timer)
        laser_offset_x = read_float(current_laser_ptr + zLaserBaseClass_offset)
        laser_offset_y = read_float(current_laser_ptr + zLaserBaseClass_offset + 0x4)
        laser_angle    = read_float(current_laser_ptr + zLaserBaseClass_angle)
        laser_length   = read_float(current_laser_ptr + zLaserBaseClass_length)
        laser_width    = read_float(current_laser_ptr + zLaserBaseClass_width)
        laser_speed    = read_float(current_laser_ptr + zLaserBaseClass_speed)
        laser_id       = read_int(current_laser_ptr + zLaserBaseClass_id)
        laser_iframes  = read_int(current_laser_ptr + zLaserBaseClass_iframes)
        laser_sprite   = read_int(current_laser_ptr + zLaserBaseClass_sprite, 2)
        laser_color    = read_int(current_laser_ptr + zLaserBaseClass_color, 2)
        
        laser_base = {
            'state': laser_state,
            'laser_type': laser_type,
            'timer': laser_timer,
            'position': (laser_offset_x, laser_offset_y), 
            'angle': laser_angle,
            'length': laser_length,
            'width': laser_width,
            'speed': laser_speed,
            'id': laser_id,
            'iframes': laser_iframes,
            'sprite': laser_sprite,
            'color': laser_color,
        }
        
        if laser_type == 0: #LINE
            line_start_pos_x = read_float(current_laser_ptr + zLaserLine_start_pos)
            line_start_pos_y = read_float(current_laser_ptr + zLaserLine_start_pos + 0x4)
            line_init_angle  = read_float(current_laser_ptr + zLaserLine_mgr_angle)
            line_max_length  = read_float(current_laser_ptr + zLaserLine_max_length)
            line_init_speed  = read_float(current_laser_ptr + zLaserLine_mgr_speed)
            line_distance    = read_float(current_laser_ptr + zLaserLine_distance)
                                    
            lasers.append(LineLaser(
                **laser_base,
                start_pos = (line_start_pos_x, line_start_pos_y),
                init_angle = line_init_angle,
                max_length = line_max_length,
                init_speed = line_init_speed, 
                distance = line_distance,
            ))
            
        elif laser_type == 1: #INFINITE
            infinite_start_pos_x   = read_float(current_laser_ptr + zLaserInfinite_start_pos)
            infinite_start_pos_y   = read_float(current_laser_ptr + zLaserInfinite_start_pos + 0x4)
            infinite_origin_vel_x  = read_float(current_laser_ptr + zLaserInfinite_velocity)
            infinite_origin_vel_y  = read_float(current_laser_ptr + zLaserInfinite_velocity + 0x4)
            infinite_default_angle = read_float(current_laser_ptr + zLaserInfinite_mgr_angle)
            infinite_angular_vel   = read_float(current_laser_ptr + zLaserInfinite_angle_vel)    
            infinite_init_length   = read_float(current_laser_ptr + zLaserInfinite_mgr_len)
            infinite_max_length    = read_float(current_laser_ptr + zLaserInfinite_final_len)
            infinite_max_width     = read_float(current_laser_ptr + zLaserInfinite_final_width)
            infinite_default_speed = read_float(current_laser_ptr + zLaserInfinite_mgr_speed)
            infinite_start_time    = read_int(current_laser_ptr + zLaserInfinite_start_time)
            infinite_expand_time   = read_int(current_laser_ptr + zLaserInfinite_expand_time)
            infinite_active_time   = read_int(current_laser_ptr + zLaserInfinite_active_time)
            infinite_shrink_time   = read_int(current_laser_ptr + zLaserInfinite_shrink_time)
            infinite_distance      = read_float(current_laser_ptr + zLaserInfinite_mgr_distance)
            
            lasers.append(InfiniteLaser(
                **laser_base,
                start_pos = (infinite_start_pos_x, infinite_start_pos_y),
                origin_vel = (infinite_origin_vel_x, infinite_origin_vel_y),
                default_angle = infinite_default_angle,
                angular_vel = infinite_angular_vel,
                init_length = infinite_init_length,
                max_length = infinite_max_length,
                max_width = infinite_max_width,
                default_speed = infinite_default_speed,
                start_time = infinite_start_time,
                expand_time = infinite_expand_time,
                active_time = infinite_active_time,
                shrink_time = infinite_shrink_time,
                distance = infinite_distance,
            ))
        
        elif laser_type == 2: #CURVE
            curve_max_length  = read_int(current_laser_ptr + zLaserCurve_max_length)
            curve_distance    = read_float(current_laser_ptr + zLaserCurve_distance)
                        
            curve_nodes = []
            current_node_ptr  = read_int(current_laser_ptr + zLaserCurve_array)
            for i in range(0, curve_max_length):
                node_pos_x = read_float(current_node_ptr + zLaserCurveNode_pos)
                node_pos_y = read_float(current_node_ptr + zLaserCurveNode_pos + 0x4)
                node_vel_x = None #seems to always be 0 for all other non-head nodes, so no need to extract
                node_vel_y = None #you can make angle/speed extraction optional too to speed things up
                node_angle = read_float(current_node_ptr + zLaserCurveNode_angle)
                node_speed = read_float(current_node_ptr + zLaserCurveNode_speed)
                
                if i == 0: 
                    node_vel_x = read_float(current_node_ptr + zLaserCurveNode_vel)
                    node_vel_y = read_float(current_node_ptr + zLaserCurveNode_vel + 0x4)
                
                curve_nodes.append(CurveNode(
                    position = (node_pos_x, node_pos_y),
                    velocity = (node_vel_x, node_vel_y),
                    angle = node_angle,
                    speed = node_speed,
                ))
                
                current_node_ptr += zLaserCurveNode_size
                
            lasers.append(CurveLaser(
                **laser_base,
                max_length = curve_max_length,
                distance = curve_distance,
                nodes = curve_nodes,
            ))
            
        elif laser_type == 3: #BEAM 
            lasers.append(Laser(**laser_base))

        current_laser_ptr = read_int(current_laser_ptr + zLaserBaseClass_next)
        
    return lasers
        

def extract_game_state(frame_id = None, real_time = None):    
    gs = GameState(
        frame_stage      = read_int(time_in_stage, rel=True),
        frame_global     = read_int(global_timer),
        seq_frame_id     = frame_id,
        seq_real_time    = real_time,
        state            = read_int(game_state, rel=True),
        mode             = read_int(game_mode, rel=True),
        score            = read_int(score, rel=True) * 10,
        lives            = read_int(lives, rel=True),
        life_pieces      = read_int(life_pieces, rel=True),
        bombs            = read_int(bombs, rel=True),
        bomb_pieces      = read_int(bomb_pieces, rel=True),
        power            = read_int(power, rel=True),
        piv              = int(read_int(piv, rel=True) / 100),
        graze            = read_int(graze, rel=True),
        boss_timer       = float(f"{read_int(zGui+zGui_bosstimer_s)}.{read_int(zGui+zGui_bosstimer_ms)}"),
        latest_SCB       = read_int(zSpellCard + zSpellcard_bonus),
        input            = read_int(input, rel=True),
        rng              = read_int(rng, rel=True),
        player_position  = (read_float(zPlayer + zPlayer_pos), read_float(zPlayer + zPlayer_pos + 0x4)),
        player_iframes   = read_int(zPlayer + zPlayer_iframes),
        player_focused   = read_int(zPlayer + zPlayer_focused) == 1,
        ddc_player_scale = read_float(zPlayer + zPlayer_scale),
        bullets          = extract_bullets() if requires_bullets else None,
        enemies          = extract_enemies() if requires_enemies else None,
        items            = extract_items() if requires_items else None,
        lasers           = extract_lasers() if requires_lasers else None,
        screen           = get_rgb_screenshot() if requires_screenshots else None,
        ddc_seija_flip   = (read_float(ddcSeijaAnm + seija_flip_x), read_float(ddcSeijaAnm + seija_flip_y)),
    )
    
    return gs

def print_game_state(gs: GameState):
    print(f"[Stage Frame #{gs.frame_stage} | Global Frame #{gs.frame_global}] SCORE: {gs.score}")
    print(f"| {gs.lives} lives ({gs.life_pieces}/3 pieces), {gs.bombs} bombs ({gs.bomb_pieces}/8 pieces), {gs.power/100} power, {gs.piv} PIV, {gs.graze} graze")
    print(f"| Player at ({round(gs.player_position[0], 2)}, {round(gs.player_position[1], 2)}) with {gs.player_iframes} invulnerability frames {'(focused movement)' if gs.player_focused else '(unfocused movement)'}")
    print(f"| Game state: {game_states[gs.state]} ({game_modes[gs.mode]})")
    print(f"| RNG value: {gs.rng}")
    
    if gs.enemies and any(enemy.is_boss for enemy in gs.enemies):
        print(f"| Boss timer: {gs.boss_timer}")
        
    if gs.ddc_seija_flip[0] != 1:
        print(f"| DDC Seija Horizontal Flip: {round(100*(-gs.ddc_seija_flip[0]+1)/2, 2)}%")
    if gs.ddc_seija_flip[1] != 1:
        print(f"| DDC Seija Vertical Flip: {round(100*(-gs.ddc_seija_flip[1]+1)/2, 2)}%")
    if gs.ddc_player_scale > 1:
        print(f"| DDC Player Scale: grew {gs.ddc_player_scale}x bigger")

    if gs.bullets:
        print("\nList of bullets:")
        print("  Position         Velocity         Speed   Angle   Radius  Color   Type")
        for bullet in gs.bullets:
            description = "• "
            description += tabulate(f"({round(bullet.position[0], 1)}, {round(bullet.position[1], 1)})", 17)
            description += tabulate(f"({round(bullet.velocity[0], 1)}, {round(bullet.velocity[1], 1)})", 17)
            description += tabulate(round(bullet.speed, 1), 8)
            description += tabulate(round(bullet.angle, 2), 8)
            description += tabulate(round(bullet.hitbox_radius, 1), 8)
            description += tabulate(get_color(bullet.bullet_type, bullet.color), 8)
            description += tabulate(sprites[bullet.bullet_type][0], 8)
            
            #not in table since rare
            if bullet.iframes > 0: 
                description += f" ({bullet.iframes} iframes)" 
                
            if bullet.show_delay > 0: 
                description += f" ({bullet.show_delay} invis frames)" 
                
            print(description)
            
    if gs.lasers:
        line_lasers = [laser for laser in gs.lasers if laser.laser_type == 0]
        infinite_lasers = [laser for laser in gs.lasers if laser.laser_type == 1]
        curve_lasers = [laser for laser in gs.lasers if laser.laser_type == 2]
        beam_lasers = [laser for laser in gs.lasers if laser.laser_type == 3]
        
        if line_lasers:
            print("\nList of segment (\"line\") lasers:")
            print("  Tail Position    Speed   Angle   Length / Max     Width   Color   Sprite")
            for laser in line_lasers:
                description = "• "
                description += tabulate(f"({round(laser.position[0], 1)}, {round(laser.position[1], 1)})", 17)
                description += tabulate(round(laser.speed, 1), 8)
                description += tabulate(round(laser.angle, 2), 8)
                description += tabulate(round(laser.length, 1), 6) + " / "
                description += tabulate(round(laser.max_length, 1), 8)
                description += tabulate(round(laser.width, 1), 8)
                description += tabulate(get_color(laser.sprite, laser.color), 8)
                description += tabulate(sprites[laser.sprite][0], 8)
                print(description)
            
        if infinite_lasers:
            print("\nList of telegraphed (\"infinite\") lasers:")
            print("  Origin Position  Origin Velocity  Angle (Vel)    Length (%)    Width (%)     Color   State (#frames left)")
            for laser in infinite_lasers:
                description = "• "
                description += tabulate(f"({round(laser.position[0], 1)}, {round(laser.position[1], 1)})", 17)
                description += tabulate(f"({round(laser.origin_vel[0], 1)}, {round(laser.origin_vel[1], 1)})", 17)
                description += tabulate(round(laser.angle, 2), 6)
                description += tabulate(f"({format(laser.angular_vel, '.3f').rstrip('0').rstrip('.')})", 9)
                description += tabulate(f"{round(laser.length, 1)} ({int(100*(laser.length-laser.init_length)/(laser.max_length-laser.init_length))}%)", 14)
                description += tabulate(f"{round(laser.width, 1)} ({int(100*laser.width/laser.max_width)}%)", 14)
                description += tabulate(get_color(laser.sprite, laser.color), 8)
                
                if laser.state == 3:
                    description += f"Telegraph ({laser.start_time - laser.timer}f)"
                elif laser.state == 4:
                    description += f"Expand ({laser.expand_time - laser.timer}f)"
                elif laser.state == 2:
                    description += f"Active ({laser.active_time - laser.timer}f)"
                elif laser.state == 5:
                    description += f"Shrink ({laser.shrink_time - laser.timer}f)"
                else:
                    description += "Unknown"
                
                print(description)
            
        if curve_lasers:
            print("\nList of curvy lasers:")
            print("  Spawn Position  Head Position   Head Velocity   HSpeed  HAngle  #Nodes  Width   Color   Sprite")
            for laser in curve_lasers:
                description = "• "
                description += tabulate(f"({round(laser.position[0], 1)}, {round(laser.position[1], 1)})", 16)
                description += tabulate(f"({round(laser.nodes[0].position[0], 1)}, {round(laser.nodes[0].position[1], 1)})", 16)
                description += tabulate(f"({round(laser.nodes[0].velocity[0], 1)}, {round(laser.nodes[0].velocity[1], 1)})", 16)
                description += tabulate(round(laser.nodes[0].speed, 1), 8)
                description += tabulate(round(laser.nodes[0].angle, 2), 8)
                description += tabulate(round(laser.max_length, 1), 8)
                description += tabulate(round(laser.width, 1), 8)
                description += tabulate(color16[laser.color], 8)
                description += tabulate(curve_sprites[laser.sprite], 8)
                print(description)
            
        if beam_lasers:
            print("\nList of beam lasers:")
            print("Note: Beam lasers are not fully supported; data may be inaccurate.")
            print("  Position         Speed   Angle   Length  Width   Color   Sprite")
            for laser in beam_lasers:
                description = "• "
                description += tabulate(f"({round(laser.position[0], 1)}, {round(laser.position[1], 1)})", 17)
                description += tabulate(round(laser.speed, 1), 8)
                description += tabulate(round(laser.angle, 2), 8)
                description += tabulate(round(laser.length, 1), 8)
                description += tabulate(round(laser.width, 1), 8)
                description += tabulate(get_color(laser.sprite, laser.color), 8)
                description += tabulate(sprites[laser.sprite][0], 8)
                print(description)
         
    if gs.enemies:
        print("\nList of enemies:")
        print("  Position         Hurtbox          Hitbox           Rotation  IFrames  HP / Max HP")
        for enemy in gs.enemies:
            description = "• "
            description += tabulate(f"({round(enemy.position[0], 1)}, {round(enemy.position[1], 1)})", 17)
            description += tabulate(f"({round(enemy.hurtbox[0], 1)}, {round(enemy.hurtbox[1], 1)})", 17)
            description += tabulate(f"({round(enemy.hitbox[0], 1)}, {round(enemy.hitbox[1], 1)})", 17)
            description += tabulate(round(enemy.rotation, 2), 10)
            description += tabulate(enemy.iframes, 9)
            description += tabulate(f"{enemy.hp} / {enemy.hp_max}", 15)
            
            if enemy.is_boss:
                if enemy.subboss_id == 0:
                    description += "(Boss)"
                else:
                    description += f"(Sub-Boss #{enemy.subboss_id})"
                
            print(description)
    
    if gs.mode == 7 and gs.items:
        print("\nList of items:")
        print("  Type            Position         Velocity")
        for item in gs.items:
            description = "• "
            description += tabulate(item.item_type + ' Item', 16)
            description += tabulate(f"({round(item.position[0], 1)}, {round(item.position[1], 1)})", 17)
            description += tabulate(f"({round(item.velocity[0], 1)}, {round(item.velocity[1], 1)})", 17)
            print(description)

#easy static stuff to grab (difficulty, stage etc) that's not worth tracking in state
def print_untracked_vars():
    print("[Bonus] Untracked values:")
    print(f"| RNG Seed: {read_int(rng_seed, rel=True)}")
    print(f"| Game Speed: {read_float(game_speed, rel=True)}")
    print(f"| Visual RNG: {read_int(visual_rng, rel=True)}")
    print(f"| Last Replay Filename: {read_string(replay_filename, 100, rel=True)}")
    print(f"| Character: {characters[read_int(character, rel=True)]}")
    print(f"| Sub-Shot: {subshots[read_int(subshot, rel=True)]}")
    print(f"| Difficulty: {difficulties[read_int(difficulty, rel=True)]}")
    print(f"| Rank: {read_int(rank, rel=True)}")
    print(f"| Stage #: {read_int(stage, rel=True)}")
    
def on_exit():
    if game_process.is_running:
        game_process.resume()
    
def parse_frame_count(expr):
    unit = expr[-1:]
    if unit.lower() not in "fs":
        return None
    
    frame_count = 0
    if unit == "s":
        try:
            frame_count = math.floor(float(expr[:-1]) * 60)
        except ValueError:
            return None
    else:
        try:
            frame_count = int(expr[:-1])
        except ValueError:
            return None
            
    return frame_count

atexit.register(on_exit)

print("================================")

if singlext_settings['only_game_world'] and read_int(game_mode, rel=True) != 7:
    print("Error: Game world not loaded (only_game_world set to True).")
    exit()
    
frame_count = 0
if seqext_settings['ingame_duration']:
    parsed_frame_count = parse_frame_count(seqext_settings['ingame_duration'])
        
    if parsed_frame_count:
        frame_count = parsed_frame_count
    else:
        print(f"Error: Couldn't parse duration '{seqext_settings['ingame_duration']}'; remember to include a unit (e.g. 150f / 12.4s).")
        print("Defaulting to single-state extraction.\n")
    
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        parsed_frame_count = parse_frame_count(arg)
        
        if parsed_frame_count:
            frame_count = parsed_frame_count
            
        elif arg == 'exact':
            exact = True #overwrites options
            
        else:
            print(f"Error: Unrecognized argument '{arg}'.")
            exit()

if not hasattr(analysis, analyzer):
    print(f"Error: Unrecognized analyzer {analyzer}; defaulting to template.")
    analyzer = 'AnalysisTemplate'
    
if frame_count < 2: #Single-State Extraction
    analysis = getattr(analysis, analyzer)()
    
    if requires_screenshots:
        get_focus()
    
    state = extract_game_state()
    analysis.step(state)
    print_game_state(state)
    
    print("================================")
    analysis.done()
    
    if singlext_settings['show_untracked']:
        print("\n================================")
        print_untracked_vars()
    
else: #State Sequence Extraction
    print(f"Extracting {frame_count} frames{' (exact mode)' if exact else ''}.")
    
    if seqext_settings['auto_unpause']:
        unpause_game()
    else:
        if seqext_settings['auto_focus']:
            get_focus()
        print("(Unpause the game to begin extraction)")
        
    analysis = getattr(analysis, analyzer)()
    start_time = time.perf_counter()
    terminated = False
    
    for i in range(frame_count):
        if terminated:
            break
            
        frame_timestamp = read_int(time_in_stage, rel=True)
        print(f"[{int(100*i/frame_count)}%] Extracting frame #{i+1} (in-stage: #{frame_timestamp})")
        
        if exact:
            game_process.suspend()
        
        state = extract_game_state(i, time.perf_counter() - start_time)
        analysis.step(state)
        
        if exact:
            game_process.resume()
            
        #busy wait for next frame
        wait_return = wait_game_frame(frame_timestamp, need_active)
        if wait_return:
            print(f"{wait_return}; terminating now.")
            terminated = True
            break
    
    if not terminated:
        print(f"[100%] Finished extraction in {round(time.perf_counter()-start_time, 2)} seconds.")
    
    if seqext_settings['auto_repause']:   
        pause_game()
        
    print("================================")
    analysis.done()