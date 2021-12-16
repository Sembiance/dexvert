import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class uaem extends Format
{
	name         = "FS-UAE Meta File";
	website      = "https://fs-uae.net/docs/options/uaem-write-flags";
	ext          = [".uaem"];
	magic        = [...TEXT_MAGIC, "FS-UAE file metadata"];
	weakMagic    = true;
	auxFiles     = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase()));
	untouched    = true;
	metaProvider = ["text"];
}
