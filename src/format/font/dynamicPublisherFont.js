import {Format} from "../../Format.js";

export class dynamicPublisherFont extends Format
{
	name           = "Dynamic Publisher Font";
	website        = "http://fileformats.archiveteam.org/wiki/Dynamic_Publisher";
	ext            = [".fnt"];
	magic          = ["Dynamic Publisher Font", /^fmt\/1779( |$)/];
	converters     = ["recoil2png"];
}
