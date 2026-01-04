import {Format} from "../../Format.js";

export class qpegDVC extends Format
{
	name       = "QPEG DVC";
	website    = "https://wiki.multimedia.cx/index.php/QPEG";
	ext        = [".dvc"];
	magic      = ["DVC video"];
	converters = ["nihav"];
}

