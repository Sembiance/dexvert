import {Format} from "../../Format.js";

export class iffCTLG extends Format
{
	name           = "Amiga IFF Catalog";
	website        = "http://fileformats.archiveteam.org/wiki/IFF";
	ext            = [".catalog"];
	forbidExtMatch = true;
	magic          = ["IFF data, CTLG message catalog", "Amiga Catalog translation format"];
	converters     = ["strings"];
}
