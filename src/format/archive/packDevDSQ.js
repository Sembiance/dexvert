import {Format} from "../../Format.js";

export class packDevDSQ extends Format
{
	name          = "PackDev DiskSqueeze";
	ext           = [".dsq", ".pkd"];
	magic         = ["PackDev compressed disk image"];
	packed        = true;
	converters    = ["uaeunp"];
}
