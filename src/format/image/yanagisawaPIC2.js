import {Format} from "../../Format.js";

export class yanagisawaPIC2 extends Format
{
	name        = "Yanagisawa PIC2";
	website     = "http://fileformats.archiveteam.org/wiki/PIC2";
	ext         = [".p2"];
	magic       = ["PIC2 bitmap"];
	weakMagic   = true;
	unsupported = true;
}
