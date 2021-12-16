import {Format} from "../../Format.js";

export class oricFont extends Format
{
	name       = "Oric Font";
	ext        = [".chs"];
	magic      = ["Oric Tape image"];
	weakMagic  = true;
	converters = ["recoil2png"];
}
