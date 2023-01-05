import {xu} from "xu";
import {Format} from "../../Format.js";

export class pageMaker extends Format
{
	name       = "Aldus/Adobe PageMaker";
	website    = "http://fileformats.archiveteam.org/wiki/PageMaker";
	ext        = [".pmd", ".pmt", ".pm3", ".pm4", ".pm5", ".pm6", ".p65"];
	magic      = ["Aldus PageMaker document", "Adobe PageMaker document"];
	converters = ["pageMaker7"];
}
