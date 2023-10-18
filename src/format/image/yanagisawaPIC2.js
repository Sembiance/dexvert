import {Format} from "../../Format.js";

export class yanagisawaPIC2 extends Format
{
	name        = "Yanagisawa PIC2";
	website     = "http://fileformats.archiveteam.org/wiki/PIC2";
	ext         = [".p2"];
	magic       = ["PIC2 bitmap"];
	weakMagic   = true;
	unsupported = true;
	notes       = `
		A request was made to add support to recoil, but that is looking unlikely: https://sourceforge.net/p/recoil/bugs/73/
		There is a PIC2 plugin for 'xv' so maybe I could create a CLI program that leverages that to convert: https://github.com/DavidGriffith/xv/blob/master/xvpic2.c`;
}
