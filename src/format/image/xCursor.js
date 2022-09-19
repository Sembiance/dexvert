import {Format} from "../../Format.js";

export class xCursor extends Format
{
	name         = "Microsoft Windows Cursor";
	website      = "http://fileformats.archiveteam.org/wiki/Xcursor";
	magic        = ["X11 cursor", "Xcursor data", "Xcursor"];
	converters   = ["xcur2png", "gimp"];
}
