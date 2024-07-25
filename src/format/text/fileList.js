import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class fileList extends Format
{
	name           = "File List";
	magic          = TEXT_MAGIC;
	weakMagic      = true;
	priority       = this.PRIORITY.LOWEST;
	ext            = [".bbs", ".lst", ".lis", ".dir", ".ind"];
	forbidExtMatch = true;
	filename       = [/^dir\.?\d+$/i, /files.\d+$/i, /^files\.txt$/i, /^\d+_index.txt$/, /^[a-zA-Z]_index.txt$/];
	untouched      = true;
	idCheck        = inputFile => inputFile.size<=xu.MB*25;	// Unlikely to ever encountere a file list this big
	metaProvider   = ["text"];
	notes          = "Some day I should try and parse these.";
}
