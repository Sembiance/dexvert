import {xu} from "xu";
import {Format} from "../../Format.js";

export class pageMaker extends Format
{
	name        = "Aldus/Adobe PageMaker";
	website     = "http://fileformats.archiveteam.org/wiki/PageMaker";
	ext         = [".pmd", ".pmt", ".pm3", ".pm4", ".pm5", ".pm6", ".p65"];
	magic       = ["Aldus PageMaker document", "Adobe PageMaker document"];
	unsupported = true;
	notes       = xu.trim`
		No known converter.
		It's a bit of a nightmare format, only well supported in the version the file was original created in.
		I have in sandbox/app/AdobePageMaker6.5 which seems to load v4 files.
		However the app pops up tons of font substitution confirmations, external file references, and other BS.
		Choosing not to bother supporting these right now, but if I start to discover a ton of them, I could rethink this.`;
}
