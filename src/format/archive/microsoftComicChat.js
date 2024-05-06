import {Format} from "../../Format.js";

export class microsoftComicChat extends Format
{
	name       = "Microsoft Comic Chat Character";
	website    = "http://fileformats.archiveteam.org/wiki/Microsoft_Comic_Chat";
	ext        = [".avb", ".bgb"];
	magic      = ["Microsoft Chat Character"];
	converters = ["deark[module:comicchat]"];
}
