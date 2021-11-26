import {Format} from "../../Format.js";

export class dynamicPublisherStamp extends Format
{
	name       = "Dynamic Publisher Stamp";
	website    = "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher";
	ext        = [".stp"];
	converters = ["recoil2png"]
}
