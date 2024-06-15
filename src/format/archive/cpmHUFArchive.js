import {Format} from "../../Format.js";

export class cpmHUFArchive extends Format
{
	name        = "CP/M HUF Archive";
	website     = "http://fileformats.archiveteam.org/wiki/HUF_(CP/M)";
	ext         = [".huf"];
	magic       = ["CP/M HUF compressed archive", "Archive: HUFF"];
	weakMagic   = true;
	unsupported = true;
}
