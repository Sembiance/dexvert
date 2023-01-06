import {xu} from "xu";
import {Format} from "../../Format.js";

export class pageMaker extends Format
{
	name       = "Aldus/Adobe PageMaker";
	website    = "http://fileformats.archiveteam.org/wiki/PageMaker";
	ext        = [".pmd", ".pmt", ".pm3", ".pm4", ".pm5", ".pm6", ".p65"];
	magic      = ["Aldus PageMaker document", "Adobe PageMaker document"];
	converters = ["pageMaker7", "pageMaker5", "pageMaker4"];	// Don't be tempted to prioritize pageMaker4 or pageMaker5 for version 4/5 documents, as PageMaker7 when it can open them prints them better
}
