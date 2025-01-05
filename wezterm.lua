-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

config.color_scheme = 'Hipster Green'

-- https://github.com/be5invis/Iosevka/
config.font = wezterm.font('Iosevka Term Curly', {weight = 'Medium'}) 
config.font_size = 14

config.initial_rows = 40
config.initial_cols = 132

-- and finally, return the configuration to wezterm
return config
