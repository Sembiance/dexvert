import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

// Fallback match for anything that is just text. This will only be matched as a last resort
export class txt extends Format
{
	name         = "Text File";
	website      = "http://fileformats.archiveteam.org/wiki/Plain_text";
	ext          = [".txt"];
	weakExt      = true;
	magic        = TEXT_MAGIC;
	idMeta       = ({macFileType, proDOSTypeCode}) => ["TEXT", "ttro"].includes(macFileType) || ["TXT"].includes(proDOSTypeCode);
	filename     = [/^file_id\.diz$/i];
	priority     = this.PRIORITY.LOWEST;
	fallback     = true;
	untouched    = true;
	metaProvider = ["text"];
}
