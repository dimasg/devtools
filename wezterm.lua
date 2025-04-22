-- Pull in the wezterm API
local wezterm = require 'wezterm'
local act = wezterm.action

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

config.default_prog = { '/usr/local/bin/fish' }

config.color_scheme = 'Hipster Green'

config.line_height = 1.2
config.font_size = 14
-- weight:
--   Thin, ExtraLight, Light, DemiLight, Book, Regular (default),
--   Medium, DemiBold, Bold, ExtraBold, Black, ExtraBlack
-- stretch:
--   UltraCondensed, ExtraCondensed, Condensed, SemiCondensed, Normal (default),
--   SemiExpanded, Expanded, ExtraExpanded, UltraExpanded
--
-- https://github.com/be5invis/Iosevka/
-- https://github.com/evilmartians/mono/
config.font = wezterm.font_with_fallback({
    {family = 'Martian Mono', weight = 'Light', stretch = 'SemiCondensed'},
    {family = 'Iosevka Term Curly', weight = 'Medium'},
    {family = 'Fira Code', weight = 'Medium'},
})

config.initial_rows = 40
config.initial_cols = 132

config.leader = { key = 'a', mods = 'CTRL', timeout_milliseconds = 1000 }

config.selection_word_boundary = ' \t\n{}"\'`';

config.keys = {
    -- show the pane selection mode, but have it swap the active and selected panes
    {
        key = '0',
        mods = 'CTRL',
        action = act.PaneSelect {
            mode = 'SwapWithActive',
        },
    },
    -- splitting
    {
        mods   = "LEADER",
        key    = "-",
        action = act.SplitVertical { domain = 'CurrentPaneDomain' }
    },
    {
        mods   = "LEADER",
        key    = "|",
        action = act.SplitHorizontal { domain = 'CurrentPaneDomain' }
    },
    {
        mods   = "LEADER",
        key    = "+",
        action = act.SplitPane {
            direction = 'Right',
            size = { Percent = 70 },
        }
    },
    -- pane switch
    {
        mods   = "LEADER",
        key = 'LeftArrow',
        action = act.ActivatePaneDirection 'Left',
    },
    {
        mods   = "LEADER",
        key = 'RightArrow',
        action = act.ActivatePaneDirection 'Right',
    },
    {
        mods   = "LEADER",
        key = 'UpArrow',
        action = act.ActivatePaneDirection 'Up',
    },
    {
        mods   = "LEADER",
        key = 'DownArrow',
        action = act.ActivatePaneDirection 'Down',
    },
    -- pane resize
    {
        key = 'h',
        mods = 'LEADER',
        action = act.AdjustPaneSize { 'Left', 5 },
    },
    {
        key = 'j',
        mods = 'LEADER',
        action = act.AdjustPaneSize { 'Down', 5 },
    },
    {
        key = 'k',
        mods = 'LEADER',
        action = act.AdjustPaneSize { 'Up', 5 }
    },
    {
        key = 'l',
        mods = 'LEADER',
        action = act.AdjustPaneSize { 'Right', 5 },
    },
    {
        key = 'z',
        mods = 'LEADER',
        action = act.TogglePaneZoomState,
    },
    -- next/previous tab
    {
        key = 'n',
        mods = 'LEADER',
        action = act.ActivateTabRelative(1),
    },
    {
        key = 'p',
        mods = 'LEADER',
        action = act.ActivateTabRelative(-1),
    },
}

-- and finally, return the configuration to wezterm
return config
-- vim: ts=4 sw=4
