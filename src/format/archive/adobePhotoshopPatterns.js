import {Format} from "../../Format.js";

export class adobePhotoshopPatterns extends Format
{
	name           = "Adobe Photoshop Patterns";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["Adobe Photoshop Pattern", "Photoshop Pattern :patps:"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="8BPT" && macFileCreator==="8BIM";
	converters     = ["nconvert[format:patps][extractAll]"];
}
