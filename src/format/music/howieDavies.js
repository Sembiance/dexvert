import {Format} from "../../Format.js";

export class howieDavies extends Format
{
	name         = "Howie Davies Module";
	website      = "http://fileformats.archiveteam.org/wiki/Howie_Davies";
	ext          = [".hd"];
	magic        = ["Howie Davies module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
