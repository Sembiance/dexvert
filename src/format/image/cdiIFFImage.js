import {Format} from "../../Format.js";

export class cdiIFFImage extends Format
{
	name        = "CD-I IFF Image";
	website     = "http://fileformats.archiveteam.org/wiki/CD-I_IFF_IMAG";
	magic       = ["CD-I IFF Image", "IFF data, CD-i image", "deark: cdi_imag"];
	notes       = "Deark has partial support, but it's the only converter that has any support at all.";
	converters  = ["deark[module:cdi_imag]"];
}
