Renumber Views On a Sheet [Malcs tools]  v.0.0.6
=============

This is part of Malcs tools

**CHECK OUT DOCUMENTATION WEBSITE:**
['Renumber Views on a sheet' Docs](http://chris-malcolm.com/projects/malcstools/p/renumber-views-on-a-sheet)

Renumber Views On a Sheet by [Chris Malcolm](http://chris-malcolm.com). The annoying part is that in revit, your view number on the sheet does not update magically when you move views around on your invisible cell grid. Furthermore, manually renumbering is sometimes a pain because you occassionally will get a nasty alert message from revit if you attempt to renumber with a duplicate number that already exists...

So this is a tool made a tool (revit python shell or dynamo player) to automatically renumber the views based on the location of the view on the sheet. 


FEATURES / GOALS
----------------
- Coming soon


KNOWN ISSUES / FUTURE IMPROVEMENTS
-----------------------------------
- Coming soon


UPDATE LOG
----------

- *v0.0.61*
	- Viewports without labels no longer break the script. BoxOutline is used in this case.
	
- *v0.0.6*
	- Diagonal Bounds line can be drawn in any which way now
	- Fixed issues if titleblock params don't exist

- *v0.0.5*
	- Initial release