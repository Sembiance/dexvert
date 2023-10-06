import {Format} from "../../Format.js";

const BSAVE_TYPES = ["cga2", "cga4", "cga16", "mcga", "wh2", "wh4", "wh16", "b256", "2col", "4col", "wh256"];		// "char" is also one, which produces an HTML file which we can't classify verify, but haven't encountered a file that uses it yet, so we omit it

export class bsave extends Format
{
	name           = "QuickBasic BSAVE Image";
	website        = "http://fileformats.archiveteam.org/wiki/BSAVE_Image";
	ext            = [".art", ".pic", ".scn", ".bsv", ".cgx", ".pix", ".dat", ".pkx", ".drw"];
	forbidExtMatch = true;
	magic          = ["QuickBasic BSAVE binary data"];
	weakMagic      = true;
	classify       = true;

	// deark can't determine what type of BSAVE format it is, so we just try em all. Yah, it produces a lot of bad output, but usually one of them IS right
	converters = [BSAVE_TYPES.map(t => `deark[opt:bsave:fmt=${t}][suffix:_${t}]`).join(" & ")];
}
