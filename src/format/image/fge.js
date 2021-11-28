import {Format} from "../../Format.js";

export class fge extends Format
{
	name       = "Floor Designer";
	website    = "http://fileformats.archiveteam.org/wiki/Floor_Designer";
	ext        = [".fge"];
	magic      = ["Atari XE Executable"];
	weakMagic  = true;
	converters = ["recoil2png"];
}
