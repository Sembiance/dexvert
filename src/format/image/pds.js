import {Format} from "../../Format.js";

export class pds extends Format
{
	name       = "Planetary Data System";
	website    = "http://fileformats.archiveteam.org/wiki/PDS";
	ext        = [".imq", ".img", ".pds"];
	magic      = ["PDS image bitmap", "PDS (JPL) image data"];
	converters = ["nconvert", "imageAlchemy"];
}
