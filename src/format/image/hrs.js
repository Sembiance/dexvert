import {Format} from "../../Format.js";

export class hrs extends Format
{
	name       = "Oric HRS";
	ext        = [".hrs", ".hir"];
	magic      = ["Oric Tape Image"];
	weakMagic  = true;
	converters = ["recoil2png"]
}
