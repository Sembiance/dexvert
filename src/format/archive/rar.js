import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const _isSupportingExtension = ext => (/\.r\d+$/i).test(ext);

export class rar extends Format
{
	name           = "Roshal Archive";
	website        = "http://fileformats.archiveteam.org/wiki/RAR";
	ext            = [".rar", ".exe"];
	forbidExtMatch = [".exe"];
	priority       = this.PRIORITY.HIGH;
	magic          = ["RAR archive data", "RAR compressed archive", "RAR Archive", "DOS RAR SFX Executable", "Installer: WinRAR Installer", "WinRAR Self Extracting archive", "application/vnd.rar", /RAR self-extracting archive/, /^RAR$/, /^RAR 5$/,
		"Embedded RAR", "RAR Archiv gefunden", "Archive: RAR", "OS/2 RAR SFXjr executable", "old RAR Archiv gefunden", "overlay: archive/rar", /^idarc: RAR( |$)/, /^geArchive: RAR_RAR( |$)/, /^fmt\/(411|613)( |$)/, /^x-fmt\/264( |$)/];
	auxFiles = (input, otherFiles) =>
	{
		const supportingFiles = otherFiles.filter(f => f.name.toLowerCase()===input.name.toLowerCase() && _isSupportingExtension(f.ext));
		return supportingFiles.length ? supportingFiles : false;
	};

	converters   = ["unrar", "unar", "sqc", "izArc[matchType:magic]", "UniExtract[matchType:magic][hasExtMatch]"];
	metaProvider = ["rarInfo"];
	keepFilename = true;
	untouched    = async ({meta, f, original}) =>
	{
		if(meta.passwordProtected)
			return true;
			
		// can only be untouched if we are a multi-part continuation file and the first-part exists in the same dir (which must be .rar)
		if(!_isSupportingExtension(f.input.ext))
			return false;

		for(const ext of [".rar", ".RAR", ".Rar"])
		{
			if(await fileUtil.exists(path.join(original.input.dir, original.input.name + ext)))
				return true;
		}
		
		return false;
	};
	post = dexState => Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="unrar")?.meta || {});
}

