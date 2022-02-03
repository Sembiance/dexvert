import {Format} from "../../Format.js";

export class cdiIFFImage extends Format
{
	name        = "CD-I IFF Image";
	magic       = ["CD-I IFF Image"];
	unsupported = true;
	notes       = "No known converter.";
}
