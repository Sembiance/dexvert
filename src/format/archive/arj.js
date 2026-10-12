import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {path} from "std";

const _isSupportingExtension = ext => (/\.[a\d]\d\d$/i).test(ext) && ext!==".001";

export class arj extends Format
{
	name           = "ARJ Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ARJ";
	ext            = [".arj", ".001", ".exe"];
	forbidExtMatch = [".001", ".exe"];
	magic          = ["ARJ compressed archive", "ARJZ compressed archive", "ARJ File Format", "ARJ archive data", "ARJ self-extracting archive", "ARJ Archiv gefunden", "Archive: ARJ", "application/x-arj", /^ARJ$/, "deark: arj (ARJ)",
		/^idarc: ARJ( |$)/, /^fmt\/610( |$)/
	];
	forbiddenMagic = ["Floppy Disk File image"];
	keepFilename   = true;
	auxFiles       = (input, otherFiles) =>
	{
		const supportingFiles = otherFiles.filter(f => f.name.toLowerCase()===input.name.toLowerCase() && _isSupportingExtension(f.ext));
		return supportingFiles.length ? supportingFiles : false;
	};
	untouched = async ({f, original}) =>
	{
		// can only be untouched if we are a multi-part continuation file and the first-part exists in the same dir (which must be .arj or .001)
		if(!_isSupportingExtension(f.input.ext))
			return false;

		for(const ext of [".arj", ".ARJ", ".001", ".Arj"])
		{
			if(await fileUtil.exists(path.join(original.input.dir, original.input.name + ext)))
				return true;
		}
		
		return false;
	};
	converters = [
		"arj", "unar"
		// arj and unar seem to handle all arj files, so no need to waste time going to windows converters
		//"sqc", "izArc", "UniExtract"
		//"deark[module:arj]"	// deark doesn't create output directories so with BILLY.ARJ LIST/BILLY.DOC is extracted as LIST_BILLY.DOC
	];
}
