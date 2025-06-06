import {Format} from "../../Format.js";

export class pds extends Format
{
	name           = "Planetary Data System";
	website        = "http://fileformats.archiveteam.org/wiki/PDS";
	ext            = [".imq", ".img", ".pds"];
	forbidExtMatch = [".img"];
	magic          = ["PDS image bitmap", "PDS (JPL) image data", "Planetary Data System :pds:"];
	converters     = ["nconvert[format:pds]", "imageAlchemy"];
}
