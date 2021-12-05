import {Format} from "../../Format.js";

export class amComposer extends Format
{
	name         = "A.M.Composer Module";
	website      = "http://fileformats.archiveteam.org/wiki/A.M._Composer_v1.2";
	ext          = [".amc"];
	magic        = ["A.M.Composer 1.2 music"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
