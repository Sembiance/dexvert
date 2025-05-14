import {Format} from "../../Format.js";

export class beamSoftwareSIFFImage extends Format
{
	name           = "Beam Software SIFF sprite/image";
	ext            = [".pim"];
	forbidExtMatch = true;
	magic          = ["Beam Software SIFF sprite/image"];
	converters     = ["wuimg"];
}
