import {Format} from "../../Format.js";

export class scummMusic extends Format
{
	name         = "SCUMM Music Module";
	ext          = [".scumm"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
