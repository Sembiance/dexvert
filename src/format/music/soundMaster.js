import {Format} from "../../Format.js";

export class soundMaster extends Format
{
	name         = "Sound Master Module";
	ext          = [".sm", ".smpro", ".sm3"];
	magic        = ["Sound Master II module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
