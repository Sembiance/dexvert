import {Format} from "../../Format.js";

export class dynamicPublisherScreen extends Format
{
	name       = "Dynamic Publisher Screen";
	website    = "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher";
	ext        = [".pct"];
	magic      = ["Dynamic Publisher Picture/Screen"];
	converters = ["recoil2png"];
}
