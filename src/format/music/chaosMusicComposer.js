import {Format} from "../../Format.js";

export class chaosMusicComposer extends Format
{
	name         = "Chaos Music Composer";
	website      = "http://justsolve.archiveteam.org/wiki/CMC";
	ext          = [".cmc", ".cm3", ".cms", ".cmr", ".dmc"];
	magic        = ["Chaos Music Composer (CMC)", "Chaos Music Composer (CMS)"];
	metaProvider = ["musicInfo"];
	converters   = ["asapconv"];
}
