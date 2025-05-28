import {Format} from "../../Format.js";

export class bsaArchive extends Format
{
	name           = "BS ARChiver";
	website        = "http://fileformats.archiveteam.org/wiki/BSArc_and_BSA";
	ext            = [".bsa", ".bsn", ".bs2"];
	forbidExtMatch = true;
	magic          = ["BSA Packing program compressed archive", "BSArc compressed archive", /^(BSArc|BSN) archive data/];
	converters     = ["bsa"];
}
