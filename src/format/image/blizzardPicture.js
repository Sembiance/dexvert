import {Format} from "../../Format.js";

export class blizzardPicture extends Format
{
	name       = "Blizzard Picture";
	website    = "http://fileformats.archiveteam.org/wiki/BLP";
	ext        = [".blp"];
	magic      = ["Blizzard Picture", "BLP :blp:"];
	converters = [
		"vibe2png", "nconvert[format:blp]", "blpngConverter",
		"paintDotNet[matchType:magic][hasExtMatch]", "uniconvertor[matchType:magic][hasExtMatch][outType:png]"
	];
}
