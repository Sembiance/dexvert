import {Format} from "../../Format.js";

export class lotusManuscriptGraphic extends Format
{
	name           = "Lotus Manuscript Graphic";
	website        = "http://fileformats.archiveteam.org/wiki/Lotus_Manuscript_graphics";
	ext            = [".bit", ".rle"];
	forbidExtMatch = true;
	magic          = ["Lotus Manuscript bitmap", "Lotus Manuscript bitmap (Alt)", "deark: lotus_mscr"];
	weakMagic      = true;
	converters     = ["deark[module:lotus_mscr]"];
}
