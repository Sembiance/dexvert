import {Format} from "../../Format.js";

export class palmDOC extends Format
{
	name           = "PalmDOC";
	website        = "http://fileformats.archiveteam.org/wiki/PalmDOC";
	ext            = [".pdb", ".prc"];
	forbidExtMatch = true;
	magic          = ["PalmDOC text document", "AportisDoc/PalmDOC", "application/x-aportisdoc", /^fmt\/396( |$)/];
	converters     = ["ebook_convert", "soffice[format:PalmDoc]"];
}
