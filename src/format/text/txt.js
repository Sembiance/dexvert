import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

// Fallback match for anything that is just text. This will only be matched as a last resort
export class txt extends Format
{
	name         = "Text File";
	website      = "http://fileformats.archiveteam.org/wiki/Text";
	magic        = TEXT_MAGIC;
	priority     = this.PRIORITY.LOWEST;
	fallback     = true;
	untouched    = true;
	metaProvider = ["text"];
}
