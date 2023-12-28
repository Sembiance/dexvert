import {Format} from "../../Format.js";

export class gimpAnimatedBrush extends Format
{
	name       = "GIMP Animated Brush";
	website    = "http://fileformats.archiveteam.org/wiki/GIMP_Animated_Brush";
	ext        = [".gih"];
	magic      = ["GIMP animated brush data"];
	converters = ["gimp"];
	notes      = "Only converts to a single 1-frame static image.";
}
