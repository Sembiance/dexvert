import {Format} from "../../Format.js";

export class soundImages extends Format
{
	name         = "Sound Images Module";
	ext          = [".tw"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
