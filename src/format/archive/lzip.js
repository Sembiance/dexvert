import {Format} from "../../Format.js";

export class lzip extends Format
{
	name           = "LZIP Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Lzip";
	ext            = [".lz"];
	forbidExtMatch = true;
	packed         = true;
	magic          = ["LZIP compressed archive", "application/x-lzip", /^lzip compressed data/];
	converters     = ["lzip", "xz", "sevenZip[renameOut]"];
}
