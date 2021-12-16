import {Program} from "../../Program.js";

export class fontforge extends Program
{
	website = "https://fontforge.org";
	package = "media-gfx/fontforge";
	
	// Script API: https://fontforge.org/docs/scripting/python/fontforge.html
	bin   = "fontforge";
	flags = {
		outType : "Which type to export to. Default: otf"
	};
	args      = async r => ["-c", `import fontforge;fontforge.open("${r.inFile()}").generate("${await r.outFile(`out.${r.flags.outType || "otf"}`)}")`];
	renameOut = true;
}
