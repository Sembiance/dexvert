import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class zip extends Format
{
	name           = "PKZip Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ZIP";
	ext            = [".zip", ".exe"];
	magic          =[
		"ZIP compressed archive", "Zip data", "Zip archive", "ZIP Format", /^PKZIP (mini-)?self-extracting 16bit DOS executable$/, /ZIP self-extracting archive/, "Zip multi-volume archive data", /^Zip$/,
		"Self-extracting zip", "ZIP Archiv gefunden", "Archive: Zip", "Zip archive, with extra data prepended", "Winzip Win32 self-extracting archive", "WinZip Self-Extractor", "QWK offline mail packet (ZIP compressed)", "End of Zip archive",
		/^x-fmt\/263( |$)/];
	idMeta         = ({macFileType}) => ["pZIP", "ZIP "].includes(macFileType);
	forbiddenMagic = ["SVArTracker module"];	// often mis-identified as a passworded zip file
	converters   = () =>
	{
		const r = ["sevenZip", "unzip", "deark[module:zip]", "deark[module:pklite]", "deark[module:zip][opt:zip:scanmode]", "unar", "sqc", "izArc"];
		
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
