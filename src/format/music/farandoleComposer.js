import {Format} from "../../Format.js";

export class farandoleComposer extends Format
{
	name         = "Farandole Composer Module";
	website      = "http://fileformats.archiveteam.org/wiki/Farandole_Composer_module";
	ext          = [".far"];
	magic        = ["Farandole Composer module", "Farandole Tracker Song", /^fmt\/723( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
