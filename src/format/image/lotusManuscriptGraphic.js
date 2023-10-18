import {Format} from "../../Format.js";

export class lotusManuscriptGraphic extends Format
{
	name       = "Lotus Manuscript Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/Lotus_Manuscript_graphics";
	ext        = [".bit", ".rle"];
	magic      = ["Lotus Manuscript bitmap"];
	converters = ["deark[module:lotus_mscr]"];
}
