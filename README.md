# Perkolator

## What?
The Fallout 4 Perkolator is a python utility for prioritizing perks and generating character builds. If you are like me and have choice paralysis every time you level up, this might help you out. You assign your priorities for each perk (and rank if you want to get that specific) and the script will figure out when it is best to unlock each perk.

## How do I use this thing?
1. Run "python perkolator.py"
2. Set your SPECIAL skills up top
3. Select a Perk from the 'Available' list
4. In the Details section, set a priority for the selected Perk's first Rank (from -1 to 11). You can also set a different priority for different Perk ranks. A priority of -1 (the default value) will inherit the priority from other ranks of that perk.
5. Click "Show Optimized Build"

## But I already have some Perks chosen!
Just select both a perk on the left side, a level on the right side, and then click the button in the middle that says "Force (Selected Perk) at (Level)". This will force that perk at that level, and the script will work around those choices. You can also use this to override the priority system if you have an edge case.

You can also force perks generated for you by the script. Select one or more Perk/Rank in the Optimized Build section, and then click "Save Selected Levels as Forced Perks"

Forced Perks show up as blue in the Optimized Build section. You can remove Forced Perks by selecting them, and then clicking "Clear Forced Perk(s)"

## To do
Currently there is no way to plan for Intensive Training, or other ways in which your SPECIAL stats might increase.