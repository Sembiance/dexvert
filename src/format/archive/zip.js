import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class zip extends Format
{
	name           = "PKZip Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ZIP";
	ext            = [".zip", ".exe"];
	magic          = ["ZIP compressed archive", "Zip archive data", "ZIP Format", /^PKZIP (mini-)?self-extracting 16bit DOS executable$/, /ZIP self-extracting archive/, "Zip multi-volume archive data", /^x-fmt\/263( |$)/];
	forbiddenMagic = ["SVArTracker module"];	// often mis-identified as a passworded zip file
	converters   = () =>
	{
		const r = ["sevenZip", "unzip", "deark", "deark[opt:zip:scanmode]", "unar", "sqc", "izArc"];
		
		// If we are macintoshjp, unar works best
		if(RUNTIME.globalFlags?.osHint?.macintoshjp)
		{
			r.removeOnce("unar");
			r.unshift("unar");
		}

		return r;
	};

	metaProvider   = ["zipInfo"];
	untouched      = dexState => dexState.hasMagics("Zip archive data (empty)");
	processed      = dexState =>
	{
		// reverse priority order
		for(const k of ["sevenZip", "unzip"])
			Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid===k)?.meta || {});
		
		if(dexState.meta.passwordProtected)
		{
			// can't do this in a 'untouched' callback because this meta data isn't available until after unzip converter has ran and the untouched method is called before converters
			dexState.untouched = true;
			return true;
		}

		return false;
	};
}
