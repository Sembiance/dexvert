import {Format} from "../../Format.js";

export class zonerCallistoMetafilePreview extends Format
{
	name           = "Zoner Callisto Metafile Preview";
	ext            = [".zmf"];
	forbidExtMatch = true;
	magic          = ["Zoner Callisto Metafile (preview) :zmf:"];
	converters     = ["nconvert[format:zmf]"];
}
