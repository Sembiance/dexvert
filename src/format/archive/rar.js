import {Format} from "../../Format.js";

export class rar extends Format
{
	name         = "Roshal Archive";
	website      = "http://fileformats.archiveteam.org/wiki/RAR";
	ext          = [".rar", ".exe"];
	magic        = ["RAR archive data", "RAR compressed archive", "RAR Archive", /RAR self-extracting archive/, /^RAR$/, /^RAR 5$/, "Embedded RAR", "RAR Archiv gefunden", /^fmt\/(411|613)( |$)/, /^x-fmt\/264( |$)/];
	auxFiles     = (input, otherFiles) =>
	{
		// if we are a whatever.r## file and there IS a whatever.rar file, don't do anything further, as the extraction of whatever.rar will get the files
		if((/\.r\d+$/i).test(input.ext) && otherFiles.some(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.rar`))
			return [];
		
		// .rar files are sometimes split into .r## files, so grab all those
		const pieces = otherFiles.filter(file => (/\.r\d+$/i).test(file.ext) && file.name.toLowerCase()===input.name.toLowerCase());
		return pieces.length>0 ? pieces : false;
	};

	converters   = ["unrar", "unar", "sqc", "izArc", "UniExtract"];
	metaProvider = ["rarInfo"];
	untouched    = dexState => !!dexState.meta.passwordProtected;
	post         = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="unrar")?.meta || {});
}

