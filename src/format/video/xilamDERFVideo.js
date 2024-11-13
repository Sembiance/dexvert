import {Format} from "../../Format.js";

export class xilamDERFVideo extends Format
{
	name        = "Xilam DERF Video";
	website     = "https://wiki.multimedia.cx/index.php/Xilam_DERF";
	ext         = [".vds", ".vdo"];
	magic       = ["Xilam DERF video"];
	weakMagic   = true;
	unsupported = true;
}
