import {Format} from "../../Format.js";

export class dynamicPublisherScreen extends Format
{
	name       = "Dynamic Publisher Screen";
	website    = "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher";
	ext        = [".pct", ".pap"];
	magic      = ["Dynamic Publisher Picture/Screen", "Dynamic Publisher screen", /^fmt\/1778( |$)/];
	converters = ["recoil2png"];
}
