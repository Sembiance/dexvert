import {Format} from "../../Format.js";

export class iconHeaven extends Format
{
	name        = "Icon Heavn";
	website     = "http://fileformats.archiveteam.org/wiki/Icon_Heaven_library";
	ext         = [".fim"];
	magic       = ["Paul van Keep's Icon Heaven icons package"];
	unsupported = true;
	notes       = "No known converter, not even on OS/2.";
}
