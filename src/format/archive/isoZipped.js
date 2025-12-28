import {Format} from "../../Format.js";

export class isoZipped extends Format
{
	name           = "ISo Zipped";
	website        = "http://fileformats.archiveteam.org/wiki/AIN";
	ext            = [".isz"];
	forbidExtMatch = true;
	magic          = ["ISo Zipped format", "Archive: Zipped ISO Disk Image (.ISZ)", "application/x-isz", /^ISO Zipped file/];
	converters     = ["ultraISO"];	// aaru issue: https://github.com/aaru-dps/Aaru/issues/255
}
