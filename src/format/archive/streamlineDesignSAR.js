import {Format} from "../../Format.js";

export class streamlineDesignSAR extends Format
{
	name           = "Streamline Archiving Utility Archive";
	website        = "http://fileformats.archiveteam.org/wiki/SAR_(Streamline_Design)";
	ext            = [".sar"];
	forbidExtMatch = true;
	magic          = ["Streamline compressed archive", "SAR Archiv gefunden", /^SAR archive data$/];
	keepFilename   = true;
	converters     = ["sar"];
}
