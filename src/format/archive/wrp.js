import {xu} from "xu";
import {Format} from "../../Format.js";

export class wrp extends Format
{
	name        = "Warp Disk Image";
	website     = "http://fileformats.archiveteam.org/wiki/WRP";
	ext         = [".wrp"];
	magic       = ["Warp compressed disk image"];
	unsupported = true;
	notes       = xu.trim`
		uaeunp says it supports it, and it will take an input .wrp and output a 'zipped.wrp' but that never converts to anything useful
		UnWarp on the amiga wants to write directly to an floppy, which we can't easily support.
		https://github.com/ipr/qXpkLib has some code to unwarp, but in 10 year old lib format for Qt.
		However it looks somewhat self contained and so we could use this code as an example: https://github.com/ipr/qUnLZX`;
}
