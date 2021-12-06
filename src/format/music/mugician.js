import {Format} from "../../Format.js";

export class mugician extends Format
{
	name         = "Digital Mugician Module";
	website      = "http://fileformats.archiveteam.org/wiki/Mugician";
	ext          = [".dmu", ".mug", ".mugician"];
	magic        = ["Mugician Module sound file", "Digital Mugician module", "Digital Mugician 2 module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
