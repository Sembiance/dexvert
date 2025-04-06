import {xu} from "xu";
import {Format} from "../../Format.js";

export class intelIndeoVideoFile extends Format
{
	name           = "Intel Indeo Video File";
	website        = "https://wiki.multimedia.cx/index.php/Indeo_IVF";
	ext            = [".ivf"];
	forbidExtMatch = true;
	magic          = ["Intel Indeo Video File"];
	converters     = ["nihav"];
}

