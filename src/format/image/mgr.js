import {Format} from "../../Format.js";

export class mgr extends Format
{
	name       = "Manager Windowing System Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/MGR_bitmap";
	ext        = [".mgr"];
	magic      = ["MGR bitmap"];
	converters = ["nconvert"];
}
