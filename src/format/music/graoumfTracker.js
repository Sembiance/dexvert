import {xu} from "xu";
import {Format} from "../../Format.js";

export class graoumfTracker extends Format
{
	name       = "Graoumf Tracker Module";
	website    = "http://fileformats.archiveteam.org/wiki/Graoumf_Tracker_module";
	ext        = [".gtk", ".gt2"];
	magic      = ["Graoumf Tracker module", "Graoumf Tracker 2 module"];
	notes      = xu.trim`
		xmp had some support for .gtk, which was commented out, but I enabled it by uncommenting it. Seems to convert the sample GTK files just fine.
		mikmod tried to add .gt2 support, but it was abandoned and is dead code now. I tried enabling it with a patch, no luck, just segfaults.
		I also tried using the original tracker http://graoumftracker2.sourceforge.net/ without much luck.`;
	converters = ["xmp"];
}
