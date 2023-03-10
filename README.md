# RimLists
A simple script to create a RimWorld modlist from a steam workshop collection url.
The modlist is intended for use with RimPy Mod Manager For Rimworld.

It is most useful when you have many mods downloaded and dont want to sort through them all in order to recreate a workshop collection.

# Usage

1) Download all desired mods from the collection on steam and the release build .exe or the main.py script.

2) Run the .exe/script, terminal window will open, follow prompts.

3) Modlist will be created at chosen path (default RimPy modlist folder) with chosen name (default collection title)

For now:
- Only includes base game, no DLCs in modlist (you can just add them back manually after modlist creation)
- Does not includes any non-steam mods (again, you can just manually add them after modlist creation)

## Requirements
- if using the py script, >=python 3.9 is needed
- Steam is installed
- RimWorld is installed via Steam
- All mods you want in the list must be downloaded - required since i cant find a way to get the mod package ids from the mod Steam ids

Install the following:
```
pip install requests 
pip install bs4
pip install beautifulsoup4
```

## Security

In order to convert the steam mod ids in the workshop collection to package ids required by RimPy, access to the script needs filesystem access, as only the downloaded mod has this context.

# Changes

If you want to make any changes please feel free to leave it as an issue and/or create a pull request.

# Testing

Tested on Windows 10 PC
