import {xu} from "xu";
import {Format} from "../../Format.js";

export class networkQRACRallyFMV extends Format
{
	name       = "Network Q RAC Rally full motion video";
	website    = "https://wiki.multimedia.cx/index.php/Network_Q_RAC_Rally_FMV";
	magic      = ["Network Q RAC Rally full motion video"];
	converters = ["na_game_tool[format:qrac-fmv]"];
}
