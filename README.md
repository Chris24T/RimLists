# RimLists
A simple script to create a RimWorld modlist from a steam workshop collection url.
The modlist is intended for use with RimPy Mod Manager For Rimworld.

# Usage

1) Download all desired mods from the collection on steam.

2) Run the script, terminal window will open prompting for a Steam Collection URL

3) Write the target workshop collection URL into the terminal and hit enter.

4) If Steam/ Rimworld / Rimpy Modlist install paths cannot be automatically resolved, terminal will prompt for manual input

5) Modlist will be created in RimPy modlist folder, or provided path if RimPy could not be found. Modlist name will be the same as the collection title - terminal will print modlist location and name

For now:
- The script assumes the user wants the modlist to be saved to RimPy modlist directory. This is fixed, unless you dont have RimPy installed.
- Only includes base game, no DLCs in modlist (you can just add them back manually after modlist creation)
- Does not includes any non-steam mods (again, you can just manually add them after modlist creation)

## Requirements
- Steam is installed
- RimWorld is installed via Steam
- All mods you want in the list must be downloaded - required since i cant find a way to get the mod package ids from the mod Steam ids

# Changes

If you want to make any changes please feel free to leave it as an issue and/or create a pull request.
