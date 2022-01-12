import {Format} from "../../Format.js";

export class dmg extends Format
{
	name       = "Apple Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/DMG";
	ext        = [".dmg"];
	priority    = this.PRIORITY.LOW;
	// for some reason, some DMG files identify as ZLIB data
	magic      = ["zlib compressed data", "ZLIB compressed data"];
	weakMagic  = true;
	converters = ["dmg2img"];
}
