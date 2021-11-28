import {Format} from "../../Format.js";

export class mapletownNetwork extends Format
{
	name      = "Mapletown Network";
	website   = "http://fileformats.archiveteam.org/wiki/Mapletown_Network";
	ext       = [".ml1", ".mx1", ".nl3"];
	byteCheck =
	[
		{ext : ".ml1", offset : 0, match : [0x31, 0x30, 0x30, 0x1A]},
		{ext : ".mx1", offset : 0, match : [0x40, 0x40, 0x40, 0x20]},
		{ext : ".nl3", offset : 0, match : [0x20, 0x20, 0x78, 0x25]}
	];
	converters = ["recoil2png"];
}


