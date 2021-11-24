import {Format} from "../../Format.js";

export class ami extends Format
{
	name       = "Amica Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Amica_Paint";
	ext        = [".ami"];
	converters = ["recoil2png", "view64"]
}
