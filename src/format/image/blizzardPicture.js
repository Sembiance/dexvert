import {Format} from "../../Format.js";

export class blizzardPicture extends Format
{
	name       = "Blizzard Picture";
	website    = "http://fileformats.archiveteam.org/wiki/BLP";
	ext        = [".blp"];
	magic      = ["Blizzard Picture"];
	converters = ["nconvert", "uniconvertor[outType:png]"];
}
