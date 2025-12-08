# CatPilot Media Assets Documentation

This document catalogs all media assets in the CatPilot project with metadata for generating replacements.

## Table of Contents

1. [Branding & Logos](#1-branding--logos)
2. [Steering Wheel Icons](#2-steering-wheel-icons)
3. [Turn Signal Icons](#3-turn-signal-icons)
4. [Distance/Following Icons](#4-distancefollowing-icons)
5. [Navigation Icons](#5-navigation-icons)
6. [Button Icons](#6-button-icons)
7. [Toggle/Settings Icons](#7-togglesettings-icons)
8. [Sound Effects](#8-sound-effects)
9. [Holiday Themes](#9-holiday-themes)
10. [Random Event Assets](#10-random-event-assets)
11. [Training Images](#11-training-images)
12. [Generated Replacements](#12-generated-replacements)

---

## Asset Summary

| Category | Count | Format | Notes |
|----------|-------|--------|-------|
| Branding/Logos | 11 | PNG, SVG, ICO | Main logo needs cat redesign |
| Steering Wheels | 20 | PNG, GIF | Themed wheels for holidays |
| Turn Signals | 90+ | PNG, GIF | Animated blinkers |
| Distance Icons | 52 | PNG, GIF | Following distance indicators |
| Navigation | 80+ | PNG, SVG | Direction arrows & markers |
| Buttons | 40+ | PNG, GIF | UI control buttons |
| Toggle Icons | 30 | PNG | Settings menu icons |
| Sounds | 52 | WAV | Engage/disengage/alerts |
| Holiday Themes | 13 themes | Mixed | Seasonal asset packs |
| Random Events | 20+ | GIF, WAV | Easter egg animations |

---

## 1. Branding & Logos

### Main Logo (NEEDS REPLACEMENT)

| Filename | Path | Size | Format | Generation Metadata |
|----------|------|------|--------|---------------------|
| main_logo.png | catpilot/system/the_pond/assets/images/ | 512x512 | PNG | **Style**: Cartoon cat face, friendly expression, green background matching #1a472a. **Elements**: Cat whiskers, pointed ears, cute eyes. **Text**: None (icon only) |
| favicon.svg | catpilot/system/the_pond/assets/images/ | 32x32 | SVG | **Style**: Simplified cat silhouette, works at small sizes |
| favicon.ico | catpilot/system/the_pond/assets/images/ | 16x16, 32x32 | ICO | **Style**: Multi-size favicon bundle |
| favicon-16x16.png | catpilot/system/the_pond/assets/images/ | 16x16 | PNG | **Style**: Minimal cat icon |
| favicon-32x32.png | catpilot/system/the_pond/assets/images/ | 32x32 | PNG | **Style**: Minimal cat icon |
| android-chrome-192x192.png | catpilot/system/the_pond/assets/images/ | 192x192 | PNG | **Style**: Cat logo for Android home screen |
| android-chrome-512x512.png | catpilot/system/the_pond/assets/images/ | 512x512 | PNG | **Style**: High-res cat logo |
| apple-touch-icon.png | catpilot/system/the_pond/assets/images/ | 180x180 | PNG | **Style**: iOS home screen icon |
| safari-pinned-tab.svg | catpilot/system/the_pond/assets/images/ | Vector | SVG | **Style**: Single color cat silhouette |

### Current Logo Reference
The current logo shows a frog. New logo should be a **friendly cat** with these characteristics:
- Orange/ginger tabby coloring OR black cat silhouette
- Automotive/tech feel (optional: subtle steering wheel, road elements)
- Works on dark green background (#1a472a)
- Matches the playful but professional tone

**Generated Replacement**: [See Generated Assets](#12-generated-replacements)

---

## 2. Steering Wheel Icons

Custom steering wheel overlays shown during driving.

| Filename | Path | Size | Format | Generation Metadata |
|----------|------|------|--------|---------------------|
| wheel.png | catpilot/assets/stock_theme/steering_wheel/ | 256x256 | PNG | **Style**: Standard circular steering wheel, gray/silver, 3-spoke design |
| wheel.png | catpilot/assets/active_theme/steering_wheel/ | 256x256 | PNG | Currently active theme wheel |

### Holiday Theme Steering Wheels

| Theme | Filename | Format | Generation Metadata |
|-------|----------|--------|---------------------|
| April Fools | wheel.png | PNG | Rainbow/silly design, jester colors |
| Christmas Week | wheel.png | PNG | Red/green, candy cane pattern, holly |
| Cinco de Mayo | wheel.png | PNG | Mexican flag colors, festive patterns |
| Easter Week | wheel.png | PNG | Pastel colors, egg patterns |
| Fourth of July | wheel.png | PNG | Red/white/blue, stars and stripes |
| Halloween Week | wheel.gif | GIF | Animated spooky wheel, orange/black, pumpkin |
| May the Fourth | wheel.png | PNG | Star Wars themed, lightsaber glow |
| New Years | wheel.png | PNG | Gold/silver, champagne bubbles, confetti |
| St Patrick's Day | wheel.png | PNG | Green, shamrocks, gold accents |
| Stitch Day | wheel.gif | GIF | Lilo & Stitch themed, blue alien |
| Thanksgiving Week | wheel.png | PNG | Orange/brown, autumn leaves, turkey |
| Valentines Day | wheel.png | PNG | Pink/red, hearts pattern |
| World Cat Day | wheel.png | PNG | Cat-themed wheel, paw prints, whiskers |

### Random Event Steering Wheels

| Filename | Path | Format | Generation Metadata |
|----------|------|--------|---------------------|
| firefox.gif | catpilot/assets/random_events/steering_wheels/ | GIF | Animated Firefox logo style, flaming fox |
| goat.gif | catpilot/assets/random_events/steering_wheels/ | GIF | Goat face, funny expression |
| great_scott.gif | catpilot/assets/random_events/steering_wheels/ | GIF | Back to the Future reference, DeLorean style |
| this_is_fine.gif | catpilot/assets/random_events/steering_wheels/ | GIF | "This is fine" dog meme, flames |
| tree_fiddy.gif | catpilot/assets/random_events/steering_wheels/ | GIF | Loch Ness Monster meme reference |
| weeb_wheel.gif | catpilot/assets/random_events/steering_wheels/ | GIF | Anime-style wheel, sparkles |

---

## 3. Turn Signal Icons

Animated turn signal indicators, typically 5-6 frame sequences.

### Signal Animation Specifications

| Property | Value |
|----------|-------|
| Size | 128x128 or 256x256 |
| Frame Count | 5-7 frames |
| Animation | Sequential blink pattern |
| Colors | Theme-dependent (orange base for standard) |

### Standard Turn Signal Frames

| Filename Pattern | Description |
|------------------|-------------|
| turn_signal_1.png through turn_signal_6.png | Progressive fill animation |
| turn_signal_blindspot.png | Warning indicator for blind spot |

### Per-Theme Signals

Each holiday theme includes a complete set of turn signal animations matching the theme colors:
- April Fools: Rainbow colors
- Christmas: Red/green alternating
- Halloween: Orange/black, pumpkin themed
- World Cat Day: Cat paw print pattern
- (etc. for all 13 themes)

---

## 4. Distance/Following Icons

Icons showing following distance mode (aggressive, standard, relaxed, traffic).

| Mode | Filename | Size | Format | Generation Metadata |
|------|----------|------|--------|---------------------|
| Aggressive | aggressive.png | 64x64 | PNG | Red color, close cars icon, exclamation |
| Standard | standard.png | 64x64 | PNG | Yellow/amber, medium spacing |
| Relaxed | relaxed.png | 64x64 | PNG | Green color, wide spacing |
| Traffic | traffic.png | 64x64 | PNG | Blue, adaptive traffic mode |

Holiday themes include animated GIF versions of these icons.

---

## 5. Navigation Icons

Direction arrows and navigation UI elements.

### Direction Icons (selfdrive/assets/navigation/)

| Pattern | Count | Description |
|---------|-------|-------------|
| direction_turn_*.png | 20+ | Turn direction arrows (left, right, slight, sharp, uturn) |
| direction_arrive_*.png | 5 | Arrival destination markers |
| direction_continue_*.png | 8 | Continue straight indicators |
| direction_fork_*.png | 6 | Fork in road options |
| direction_merge_*.png | 6 | Highway merge indicators |
| direction_ramp_*.png | 8 | On/off ramp directions |

### Size Specifications
- Standard: 64x64 PNG
- High-res: 128x128 PNG
- Colors: White arrows on transparent background

---

## 6. Button Icons

UI control buttons for the interface.

| Filename | Path | Size | Description |
|----------|------|------|-------------|
| button_home.png | selfdrive/assets/images/ | 48x48 | Home navigation button |
| button_settings.png | selfdrive/assets/images/ | 48x48 | Settings gear icon |
| button_flag.png | selfdrive/assets/images/ | 48x48 | Destination flag marker |

Holiday themes include animated button_home.gif and button_flag.gif versions.

---

## 7. Toggle/Settings Icons

Icons used in the settings/toggles menu.

| Filename | Size | Format | Description | Generation Metadata |
|----------|------|--------|-------------|---------------------|
| icon_cat.png | 64x64 | PNG | Cat mascot icon | Cute cat face, matches branding |
| icon_steering.png | 64x64 | PNG | Steering control | Steering wheel symbol |
| icon_vehicle.png | 64x64 | PNG | Vehicle settings | Car silhouette |
| icon_map.png | 64x64 | PNG | Map/navigation | Folded map icon |
| icon_speed_map.png | 64x64 | PNG | Speed limit maps | Speedometer + map |
| icon_lane.png | 64x64 | PNG | Lane keeping | Road lanes symbol |
| icon_model.png | 64x64 | PNG | AI model selection | Neural network icon |
| icon_sound.png | 64x64 | PNG | Sound settings | Speaker icon |
| icon_mute.png | 64x64 | PNG | Mute toggle | Crossed speaker |
| icon_display.png | 64x64 | PNG | Display settings | Monitor icon |
| icon_device.png | 64x64 | PNG | Device settings | Comma device icon |
| icon_system.png | 64x64 | PNG | System settings | Gear/cog icon |
| icon_personality.png | 64x64 | PNG | Driving personality | Face/persona icon |
| icon_conditional.png | 64x64 | PNG | Conditional features | If/then logic icon |
| icon_lateral_tune.png | 64x64 | PNG | Lateral tuning | Left-right arrows |
| icon_longitudinal_tune.png | 64x64 | PNG | Longitudinal tuning | Up-down arrows |
| icon_quality_of_life.png | 64x64 | PNG | QoL features | Comfort icon |
| icon_customization.png | 64x64 | PNG | Customization | Palette/brush icon |
| icon_rainbow.png | 64x64 | PNG | Color themes | Rainbow arc |
| icon_random.png | 64x64 | PNG | Random features | Dice icon |
| icon_random_themes.png | 64x64 | PNG | Random theme picker | Shuffle icon |
| icon_calendar.png | 64x64 | PNG | Holiday scheduling | Calendar icon |
| icon_light.png | 64x64 | PNG | Light settings | Lightbulb |
| icon_green_light.png | 64x64 | PNG | Green light alerts | Traffic light |
| icon_message.png | 64x64 | PNG | Messages/alerts | Speech bubble |
| icon_vtc.png | 64x64 | PNG | Vision Turn Control | Eye + curve |
| icon_always_on_lateral.png | 64x64 | PNG | Always-on lateral | Lock + steering |
| icon_advanced_device.png | 64x64 | PNG | Advanced device | Device + gear |
| icon_advanced_lateral_tune.png | 64x64 | PNG | Advanced lateral | Detailed tuning |
| icon_advanced_longitudinal_tune.png | 64x64 | PNG | Advanced longitudinal | Detailed tuning |

---

## 8. Sound Effects

Audio files for system events.

### Core Sounds (selfdrive/assets/sounds/)

| Filename | Duration | Description | Generation Notes |
|----------|----------|-------------|------------------|
| engage.wav | ~0.5s | System engaged | Pleasant chime, ascending tone |
| disengage.wav | ~0.5s | System disengaged | Soft descending tone |
| warning_soft.wav | ~1s | Soft warning | Gentle alert beep |
| warning_immediate.wav | ~1s | Urgent warning | Louder, attention-grabbing |
| prompt.wav | ~0.5s | User prompt | Question/notification tone |
| prompt_distracted.wav | ~1s | Driver distraction | Alert to pay attention |
| refuse.wav | ~0.5s | Action refused | Negative feedback tone |

### Random Event Sounds (catpilot/assets/random_events/sounds/)

| Filename | Description |
|----------|-------------|
| angry.wav | Angry sound effect |
| continued.wav | Continuation sound |
| dejaVu.wav | Deja vu meme audio |
| doc.wav | Doc Brown reference |
| fart.wav | Comedic fart sound |
| firefox.wav | Firefox sound |
| goat.wav | Goat bleat |
| hal9000.wav | HAL 9000 "I'm sorry Dave" |
| mail.wav | "You've got mail" |
| nessie.wav | Loch Ness sound |
| noice.wav | "Noice" meme |
| this_is_fine.wav | Fire crackling |
| uwu.wav | UwU anime sound |

### Holiday Theme Sounds

Each theme includes custom engage/disengage sounds:
- Christmas: Sleigh bells
- Halloween: Spooky sounds
- May the Fourth: Lightsaber sounds
- New Years: Party horn
- (etc.)

---

## 9. Holiday Themes

Complete asset packs for seasonal themes.

| Theme | Active Dates | Assets Included |
|-------|--------------|-----------------|
| new_years | Jan 1-2 | Steering wheel, signals, distance icons, sounds, buttons |
| valentines_day | Feb 14-15 | Hearts theme, pink/red colors |
| st_patricks_day | Mar 17-18 | Shamrocks, green theme |
| april_fools | Apr 1 | Rainbow/silly theme |
| easter_week | Easter +/- 3 days | Pastel eggs theme |
| cinco_de_mayo | May 5 | Mexican celebration theme |
| may_the_fourth | May 4 | Star Wars theme |
| stitch_day | Jun 26 | Lilo & Stitch theme |
| fourth_of_july | Jul 4 | American patriotic theme |
| world_cat_day | Aug 8 | **Cat-themed assets** |
| halloween_week | Oct 24-31 | Spooky orange/black theme |
| thanksgiving_week | Thanksgiving +/- 3 days | Autumn/harvest theme |
| christmas_week | Dec 20-26 | Red/green holiday theme |

### Theme Directory Structure
```
catpilot/assets/holiday_themes/{theme_name}/
├── steering_wheel/
│   └── wheel.png (or wheel.gif)
├── signals/
│   ├── turn_signal_1.png through turn_signal_6.png
│   └── turn_signal_blindspot.png
├── distance_icons/
│   ├── aggressive.png (or .gif)
│   ├── standard.png
│   ├── relaxed.png
│   └── traffic.png
├── icons/
│   ├── button_home.gif
│   ├── button_flag.gif
│   └── button_settings.png
└── sounds/
    ├── engage.wav
    ├── disengage.wav
    └── startup.wav (optional)
```

---

## 10. Random Event Assets

Easter egg animations and sounds that appear randomly.

### Random Steering Wheels
Animated GIFs that replace the steering wheel temporarily:
- firefox.gif - Firefox logo animation
- goat.gif - Goat face
- great_scott.gif - Back to the Future reference
- this_is_fine.gif - Meme dog in fire
- tree_fiddy.gif - Loch Ness Monster
- weeb_wheel.gif - Anime-style sparkles

### Random Icons
- button_home.gif - Animated home button

---

## 11. Training Images

Onboarding/training screens (selfdrive/assets/training/).

| Filename | Description |
|----------|-------------|
| step0.png through step18.png | 19 training screen images |

**Size**: Full screen resolution (1920x1080 or device-specific)
**Content**: Instructions for using the driver assistance system

---

## 12. Generated Replacements

All generated images are stored in `attached_assets/generated_images/`

### Branding & Logos

| Image | Filename | Description | Preview |
|-------|----------|-------------|---------|
| Main Logo | catpilot_main_logo_icon.png | Primary CatPilot logo - friendly orange tabby cat | ![Logo](../attached_assets/generated_images/catpilot_main_logo_icon.png) |
| Favicon | catpilot_favicon_small_icon.png | Minimal cat silhouette for browser favicon | ![Favicon](../attached_assets/generated_images/catpilot_favicon_small_icon.png) |
| Mascot | catpilot_driving_cat_mascot.png | Cat driving with steering wheel | ![Mascot](../attached_assets/generated_images/catpilot_driving_cat_mascot.png) |

**Status**: Main logo has been applied to `catpilot/system/the_pond/assets/images/main_logo.png`

### Steering Wheels

| Image | Filename | Theme | Preview |
|-------|----------|-------|---------|
| Cat Wheel | cat-themed_steering_wheel_icon.png | Standard cat-themed wheel with paw prints | ![Cat Wheel](../attached_assets/generated_images/cat-themed_steering_wheel_icon.png) |
| World Cat Day | world_cat_day_steering_wheel.png | August 8 World Cat Day celebration | ![Cat Day](../attached_assets/generated_images/world_cat_day_steering_wheel.png) |
| Halloween | halloween_steering_wheel_icon.png | Spooky pumpkin theme | ![Halloween](../attached_assets/generated_images/halloween_steering_wheel_icon.png) |
| Christmas | christmas_steering_wheel_icon.png | Festive red/green holiday | ![Christmas](../attached_assets/generated_images/christmas_steering_wheel_icon.png) |
| Star Wars | star_wars_steering_wheel_icon.png | May the Fourth lightsaber theme | ![StarWars](../attached_assets/generated_images/star_wars_steering_wheel_icon.png) |

### Turn Signals & Indicators

| Image | Filename | Description | Preview |
|-------|----------|-------------|---------|
| Right Arrow | turn_signal_right_arrow.png | Standard orange turn signal | ![Signal](../attached_assets/generated_images/turn_signal_right_arrow.png) |
| Cat Paw Signal | cat_paw_turn_signal_icon.png | Cat paw themed blinker | ![Paw](../attached_assets/generated_images/cat_paw_turn_signal_icon.png) |

### Distance Icons

| Image | Filename | Mode | Preview |
|-------|----------|------|---------|
| Aggressive | aggressive_distance_mode_icon.png | Close following (red) | ![Aggressive](../attached_assets/generated_images/aggressive_distance_mode_icon.png) |
| Relaxed | relaxed_distance_mode_icon.png | Far following (green) | ![Relaxed](../attached_assets/generated_images/relaxed_distance_mode_icon.png) |

### Full Generated Assets List

```
attached_assets/generated_images/
├── catpilot_main_logo_icon.png      (729 KB) - Main branding logo
├── catpilot_favicon_small_icon.png  (354 KB) - Browser favicon
├── catpilot_driving_cat_mascot.png  (902 KB) - Mascot illustration
├── cat-themed_steering_wheel_icon.png (942 KB) - Standard cat wheel
├── world_cat_day_steering_wheel.png (1.0 MB) - World Cat Day theme
├── halloween_steering_wheel_icon.png (1.0 MB) - Halloween theme
├── christmas_steering_wheel_icon.png (928 KB) - Christmas theme
├── star_wars_steering_wheel_icon.png (1.1 MB) - May the Fourth theme
├── turn_signal_right_arrow.png      (694 KB) - Turn signal icon
├── cat_paw_turn_signal_icon.png     (941 KB) - Cat paw blinker
├── aggressive_distance_mode_icon.png (307 KB) - Aggressive mode
└── relaxed_distance_mode_icon.png   (448 KB) - Relaxed mode
```

---

## Asset Generation Guidelines

### For AI Image Generation

When generating replacement assets, use these prompts:

**Logo/Branding**:
```
Style: Flat design, vector-style illustration
Subject: Friendly cartoon cat face
Colors: Orange tabby OR black silhouette, green accent (#1a472a)
Background: Transparent or dark green
Mood: Playful but professional, tech-forward
```

**Steering Wheels**:
```
Style: Circular steering wheel, 3-spoke design
Size: 256x256 pixels
Background: Transparent
Theme-specific: Add holiday/theme elements
```

**Icons**:
```
Style: Flat design, single color or minimal palette
Size: 64x64 pixels
Background: Transparent
Line weight: 2-3px for consistency
```

---

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Theme assets | {theme_name}/{category}/{asset}.{ext} | christmas_week/sounds/engage.wav |
| Toggle icons | icon_{feature}.png | icon_steering.png |
| Navigation | direction_{action}_{direction}.png | direction_turn_left.png |
| Signals | turn_signal_{frame}.png | turn_signal_3.png |

---

*Document generated for CatPilot rebranding project - December 2025*
