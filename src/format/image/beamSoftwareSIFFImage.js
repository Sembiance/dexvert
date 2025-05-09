import {Format} from "../../Format.js";

export class beamSoftwareSIFFImage extends Format
{
	name           = "Beam Software SIFF sprite/image";
	website        = "http://fileformats.archiveteam.org/wiki/DIV_Games_Studio";
	ext            = [".pim"];
	forbidExtMatch = true;
	magic          = ["Beam Software SIFF sprite/image"];
	converters     = ["wuimg"];
}
