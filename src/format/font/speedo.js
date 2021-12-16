import {Format} from "../../Format.js";

export class speedo extends Format
{
	name        = "Speedo Font";
	website     = "http://fileformats.archiveteam.org/wiki/Speedo";
	ext         = [".spd"];
	magic       = ["X11 Speedo font data", "Bitstream Speedo font"];
	unsupported = true;
}
