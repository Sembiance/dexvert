import {Format} from "../../Format.js";

export class zip extends Format
{
	name           = "PKZip Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ZIP";
	ext            = [".zip", ".exe"];
	magic          = ["ZIP compressed archive", "Zip archive data", "ZIP Format", /^PKZIP (mini-)?self-extracting 16bit DOS executable$/, /ZIP self-extracting archive/, "Zip multi-volume archive data"];
	forbiddenMagic = ["SVArTracker module"];	// often mis-identified as a passworded zip file
	converters     = ["unzip", "deark", "deark[opt:zip:scanmode]", "sevenZip", "unar", "UniExtract"];
	metaProvider   = ["zipInfo"];
	untouched      = dexState => dexState.ids.some(id => id.magic==="Zip archive data (empty)");
	post           = dexState =>
	{
		Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="unzip")?.meta || {});
		if(dexState.meta.passwordProtected)
		{
			// can't do this in a 'untouched' callback because the data isn't available until after the converters have tried to run
			dexState.processed = true;
			dexState.untouched = true;
		}
	};
}
