import {Format} from "../../Format.js";

export class ldpic extends Format
{
	name       = "BBC Micro LdPic Image";
	website    = "http://fileformats.archiveteam.org/wiki/LdPic";
	ext        = [".bbg"];
	converters = ["recoil2png"]
}
