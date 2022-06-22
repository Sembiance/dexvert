import {Format} from "../../Format.js";

export class softdiskLibrary extends Format
{
	name       = "Softdisk LIBrary Game Data Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/Softdisk_Library_Format";
	ext        = [".cmb", ".shl"];
	magic      = ["Softdisk LIBrary game data archive", "Softlib archive"];
	converters = ["softlib"];
}
