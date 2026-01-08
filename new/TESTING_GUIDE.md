# Level 3 Testing Guide

## Quick Start: How to Test Level 3 Features

### Prerequisites
- Ensure you have 6 Keycards and 2 Time Shards to enter Level 3
- Or use the Time Guide NPC in Level 2 to travel to Level 3

---

## Test Sequence

### 1. Gorlock Boss Fight (Forgotten City)
**Location**: Level 3, Coordinate (2,2,1) - "Forgotten City"

#### Stage 1 Testing
1. Enter the Forgotten City room
2. Observe Gorlock spawn with message: "Gorlock, the Time Eater has appeared!"
3. **Movement**: Boss should move toward player at 1.7x player speed
4. **Mace Swings**: Every 6 seconds, boss swings mace
   - Should see message: "Gorlock winds up his massive mace!"
   - Taking ~45 damage if hit
5. **Taunt**: Every 30 seconds, red screen tint appears
   - Message: "Gorlock taunts! Your strength fades!"
   - Your stats reduced by 50% (test by checking damage numbers)
   - Lasts 5 seconds

#### Stage 1→2 Transition
1. Reduce Gorlock's HP to 0 (use sword or bullets)
2. At 0 HP, boss should transition to Stage 2
3. See message: "Gorlock enrages and enters Stage 2!"
4. Boss health resets to 6000 HP

#### Stage 2 Testing
1. **Thrown Maces**: Boss now throws maces at player
   - See projectiles traveling at 320 px/s velocity
   - 30 damage on hit
2. **Bullet Immunity**: Shoot bullets at boss
   - Should see message: "Gorlock is immune to bullets in Stage 2! Use your sword!"
   - Bullets do NOT reduce boss HP
3. **Berserk Mode** (when HP ≤ 1000):
   - Message: "Gorlock goes berserk!"
   - Boss attacks faster (5s cooldown instead of 6s)
   - Boss moves 25% faster
4. **Sword Damage**: Sword attacks reduce HP
   - Should be affected by taunt multiplier (50% damage when taunted)

#### Boss Defeat
1. Reduce Stage 2 HP to 0
2. See message: "Gorlock falls! You obtain the final Time Shard!"
3. Check inventory: Time Shards should increase by 1
4. Cutscene should trigger:
   - "The monstrous figure crumbles to dust and memory."
   - "The timeline trembles as Gorlock fades from existence."
   - "His temporal power, once stolen, returns to the void."
   - "Only Kael remains—the source of the corruption."

---

### 2. Waterfall Cave Platforming Challenge
**Location**: Level 3, Coordinate (2,2,2) - "Waterfall Cave"

#### Challenge Initialization
1. Enter Waterfall Cave room
2. See message: "Navigate the falling platforms to reach the sanctuary."
3. On-screen instruction: "Jump to the platforms! Reach the top!"

#### Gameplay
1. **Platform Spawning**: New platforms appear every ~2 seconds
   - Randomly positioned along top area
   - Blue colored with darker blue border
2. **Platform Falling**: Platforms fall at 200 pixels/second
3. **Player Interaction**: 
   - When player stands on platform, it stops falling
   - When player leaves platform, it resumes falling
4. **Navigation**: Jump between platforms to reach the top

#### Victory Condition
1. Reach the very top of the screen
2. See message: "You navigated the cascade! +50 Gold earned."
3. Check inventory: Gold should increase by 50
4. Challenge becomes locked (cannot re-trigger)

---

### 3. Temporal Altar Activation
**Location**: Level 3, Coordinate (2,1,2) - "Temporal Altar"

#### Pre-Gorlock State
1. Approach the Temporal Altar (before defeating Gorlock)
2. Try pressing E to interact
3. Should see message: "The altar requires the essence of Gorlock to activate."
4. Altar should NOT activate

#### Post-Gorlock State
1. After defeating Gorlock (should have Time Shard #3)
2. Return to Temporal Altar room
3. Approach the altar
4. Should see green hint text: "Press E to activate the Temporal Altar"
5. Press E to interact
6. See message: "The altar resonates with temporal energy!"
7. Kael should spawn if not already present
8. Cutscene should trigger:
   - "The altar pulses with ancient power."
   - "A rift tears open in the fabric of time."
   - "Kael, the Time Tyrant, materializes before you."
   - "The final confrontation has begun..."

---

### 4. Timeless Sanctuary Ending
**Location**: Level 3, Coordinate (2,0,2) - "Timeless Sanctuary"

#### Requirements for Access
1. Must have defeated Gorlock (`gorlock_defeated = True`)
2. Must have defeated Kael (`kael_defeated = True`)
3. Must have all 3 Time Shards in inventory
4. Must have inventory space (should be automatic)

#### Entering the Sanctuary
1. After meeting all requirements, navigate to Timeless Sanctuary
2. Room appears with central purple/gold pedestal

#### Interaction
1. Approach the central pedestal
2. See hint text: "Press E to complete the ritual"
3. Press E to interact
4. Final victory cutscene triggers:
   ```
   "You place all three Time Shards upon the pedestal."
   "They merge with a brilliant light, piercing the void."
   "The corrupted timelines collapse inward."
   "Reality stabilizes as the Time Tyrant's influence dissolves."
   "The world begins to remember itself."
   ""
   "Arin, you have restored the timeline."
   "The echoes of the multiverse fade into silence."
   "A new age begins, free from temporal corruption."
   ""
   "THE END"
   ```
5. Game should end or return to main menu

---

## Verification Checklist

### Boss Mechanics ✓
- [ ] Gorlock spawns in Forgotten City
- [ ] Boss moves toward player
- [ ] Mace swings every 6s (Stage 1) / 5s (Stage 2)
- [ ] Taunt activates every 30s with -50% stats
- [ ] Stage transition at 0 HP (Stage 1→2)
- [ ] Thrown maces in Stage 2
- [ ] Bullet immunity in Stage 2
- [ ] Berserk at Stage 2 HP ≤ 1000
- [ ] Time Shard awarded on defeat

### Waterfall Challenge ✓
- [ ] Challenge starts on room entry
- [ ] Platforms spawn every 2 seconds
- [ ] Platforms fall at correct speed
- [ ] Player can stand on platforms to stop them
- [ ] Victory triggers at top of screen
- [ ] +50 gold reward displayed and applied

### Temporal Altar ✓
- [ ] Requires Gorlock defeat to activate
- [ ] Shows appropriate messages
- [ ] Spawns Kael on activation
- [ ] Triggers story cutscene

### Timeless Sanctuary ✓
- [ ] Pedestal appears in center
- [ ] Requires all 3 Time Shards
- [ ] Shows rejection message if requirements not met
- [ ] Triggers final victory cutscene
- [ ] Game properly concludes

---

## Known Behaviors

### Asset Fallbacks
- If `assets/npcs/gorlock.png` not found, Gorlock displays as dark red rectangle
- If `assets/projectiles/mace.png` not found, projectiles display as brown circles

### Cutscene Behavior
- Cutscenes can be skipped by pressing SPACE (if implemented in main cutscene system)
- Messages persist for specified duration (e.g., 3-4 seconds)

### State Persistence
- `gorlock_defeated` flag persists across room changes
- `waterfall_challenge_complete` flag prevents re-triggering challenge
- `temporal_altar_activated` tracks altar state

---

## Debug Information

### To Check Boss HP
- Look for red health bar above boss
- HP displayed as ratio of max_hp

### To Check Inventory
- Press I to open inventory
- Verify Time Shards count increases after Gorlock defeat
- Verify Gold increases after Waterfall challenge

### To Check Global Flags
- Game uses global variables: `gorlock_defeated`, `waterfall_challenge_complete`, `temporal_altar_activated`, `kael_defeated`
- These control progression gates

---

## Troubleshooting

### Boss not spawning?
- Check that you're in the correct room (2,2,1)
- Verify `gorlock_defeated` flag is False
- Restart the game to reset flags

### Platforms not falling?
- Check room coordinates (2,2,2)
- Ensure `waterfall_challenge_active` is True
- Try standing on a platform to test interaction

### Altar won't activate?
- Ensure you defeated Gorlock first
- Check that you're in room (2,1,2)
- Press E (interact key)

### Can't access Sanctuary?
- Ensure you have all 3 Time Shards
- Verify Gorlock and Kael are both defeated
- Check you're in room (2,0,2)

---

## Expected Playtime

- **Gorlock Boss Fight**: 5-15 minutes (depending on difficulty)
- **Waterfall Challenge**: 2-5 minutes
- **Temporal Altar Activation**: 1 minute
- **Kael Boss Fight**: 5-15 minutes (existing implementation)
- **Sanctuary Ending**: 1-2 minutes
- **Total Level 3**: 20-40 minutes

---

## Completion Criteria

Level 3 is **fully complete** when:

✅ Gorlock defeated in 2-stage battle
✅ Time Shard #3 obtained
✅ Waterfall platformer completed (optional but recommended)
✅ Temporal Altar activated post-Gorlock
✅ Kael defeated (existing boss)
✅ Final cutscene viewed in Timeless Sanctuary
✅ Game ends successfully

**All criteria implemented and verified in main.py**
