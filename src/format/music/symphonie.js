import {Format} from "../../Format.js";

export class symphonie extends Format
{
	name         = "Symphonie Module";
	ext          = [".symmod"];
	magic        = ["Symphonie SymMOD music file", "Symphonie Module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
