import {Format} from "../../Format.js";

export class sidMon extends Format
{
	name         = "SidMon Module";
	website      = "http://fileformats.archiveteam.org/wiki/Sidmon";
	ext          = [".sid"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
