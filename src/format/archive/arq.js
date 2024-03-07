import {Format} from "../../Format.js";

export class arq extends Format
{
	name       = "ARQ Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ARQ";
	ext        = [".arq"];
	magic      = ["ARQ archive", "ARQ Archiv gefunden"];
	converters = ["arq"];
}
