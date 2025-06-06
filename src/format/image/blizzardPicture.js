import {Format} from "../../Format.js";

export class blizzardPicture extends Format
{
	name       = "Blizzard Picture";
	website    = "http://fileformats.archiveteam.org/wiki/BLP";
	ext        = [".blp"];
	magic      = ["Blizzard Picture", "BLP :blp:"];
	converters = ["nconvert[format:blp]", "blpngConverter", "paintDotNet", "uniconvertor[outType:png]"];
}
