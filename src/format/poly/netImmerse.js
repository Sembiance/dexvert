import {Format} from "../../Format.js";

export class netImmerse extends Format
{
	name        = "NetImmerse File";
	ext         = [".nif"];
	magic       = ["NetImmerse file format"];
	unsupported = true;
}
