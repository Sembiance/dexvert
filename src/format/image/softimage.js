import {Format} from "../../Format.js";

export class softimage extends Format
{
	name           = "Softimage PIC Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Softimage_PIC";
	ext            = [".soft", ".pic"];
	forbidExtMatch = true;
	magic          = ["Softimage Picture bitmap", /^fmt\/1167( |$)/];
	converters     = ["nconvert"];	// iconvert also supports this but often just creates a black image
}
