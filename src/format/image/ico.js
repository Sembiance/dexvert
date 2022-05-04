import {Format} from "../../Format.js";

export class ico extends Format
{
	name       = "Microsoft Windows Icon File";
	website    = "http://fileformats.archiveteam.org/wiki/ICO";
	ext        = [".ico"];
	magic      = ["Windows Icon", "MS Windows icon resource", "Icon File Format", /^x-fmt\/418( |$)/];
	trustMagic = true;

	// ICO file has multiple sub icons, which deark handles well. Fallback to nconvert
	converters = ["deark", "nconvert", "gimp", "hiJaakExpress", "canvas"];
}
