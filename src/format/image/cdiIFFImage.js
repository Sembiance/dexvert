import {Format} from "../../Format.js";

export class cdiIFFImage extends Format
{
	name        = "CD-I IFF Image";
	website     = "http://fileformats.archiveteam.org/wiki/CD-I_IFF_IMAG";
	magic       = ["CD-I IFF Image"];
	unsupported = true;
	notes       = "No known converter.";
}
