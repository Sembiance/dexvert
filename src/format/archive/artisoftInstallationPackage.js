import {Format} from "../../Format.js";

export class artisoftInstallationPackage extends Format
{
	name           = "Artisoft installation Package";
	website        = "http://fileformats.archiveteam.org/wiki/ARTIPACK";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["Artisoft installation Package", "deark: artipack"];
	converters     = ["deark[module:artipack]"];
}
