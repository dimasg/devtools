-- Pull in the wezterm API
local wezterm = require 'wezterm'
local act = wezterm.action

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

config.color_scheme = 'Hipster Green'

-- https://github.com/be5invis/Iosevka/
config.font = wezterm.font('Iosevka Term Curly', {weight = 'Medium'}) 
config.font_size = 14

config.initial_rows = 40
config.initial_cols = 132

config.keys = {
    -- show the pane selection mode, but have it swap the active and selected panes
    {
        key = '0',
        mods = 'CTRL',
        action = act.PaneSelect {
            mode = 'SwapWithActive',
        },
    },
}

-- and finally, return the configuration to wezterm
return config
-- vim: ts=4 sw=4
