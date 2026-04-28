import {Format} from "../../Format.js";

export class lotusSmartIcon extends Format
{
	name           = "Lotus Smart Icon";
	ext            = [".smi"];
	forbidExtMatch = true;
	magic          = ["Lotus Smart Icon"];
	weakMagic      = true;
	unsupported    = true;	// these are NOT raster images, rather meta data that just give toolbar definitions. see legacy/lotusSmartIcon for more info
}
