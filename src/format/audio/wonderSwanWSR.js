import {Format} from "../../Format.js";

export class wonderSwanWSR extends Format
{
	name        = "WonderSwan WSR Audio";
	website     = "http://fileformats.archiveteam.org/wiki/WSR";
	ext         = [".wsr"];
	magic       = ["WonderSwan WSR Audio"];
	unsupported = true;
}
