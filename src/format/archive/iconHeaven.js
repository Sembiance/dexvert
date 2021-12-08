import {Format} from "../../Format.js";

export class iconHeaven extends Format
{
	name        = "Icon Heavn";
	website     = "http://fileformats.archiveteam.org/wiki/Icon_Heaven_library";
	ext         = [".fim"];
	magic       = ["Paul van Keep's Icon Heaven icons package"];
	unsupported = true;
	notes       = "Could support it by using icon heaven under an emulated OS/2 instance. NOTE, if the only thing in this is images, then it should be moved to image family";
}
