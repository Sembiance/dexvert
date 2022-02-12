import {Format} from "../../Format.js";

export class herad extends Format
{
	name         = "Herad System";
	ext          = [".sqx", ".agd", ".sdb"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
