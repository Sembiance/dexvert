import {Format} from "../../Format.js";

export class iceStar extends Format
{
	name       = "Atari ICE* Image";
	website    = "http://fileformats.archiveteam.org/wiki/ICE*";
	ext        = [".icn", ".imn", ".ipc", ".ip2"];
	converters = ["recoil2png"]
}
