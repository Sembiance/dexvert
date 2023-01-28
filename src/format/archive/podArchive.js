import {Format} from "../../Format.js";

export class podArchive extends Format
{
	name       = "POD Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/POD_Format";
	ext        = [".pod"];
	magic      = ["POD Archive"];
	weakMagic  = true;
	converters = ["gamearch"];
}
