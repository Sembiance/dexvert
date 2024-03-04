import {Format} from "../../Format.js";

export class infoFile extends Format
{
	name           = "InfoFile Database File";
	website        = "http://fileformats.archiveteam.org/wiki/FLR";
	ext            = [".flr"];
	forbidExtMatch = true;
	magic          = ["InfoFile database", /^fmt\/1785( |$)/];
	weakMagic      = true;
	notes          = "Very obscure amiga database program.";
	converters     = ["strings"];
}
