import {Format} from "../../Format.js";

export class soundControl extends Format
{
	name         = "Sound Control Module";
	ext          = [".sc"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
