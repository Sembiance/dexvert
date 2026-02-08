import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class innoSetupInstaller extends Format
{
	name           = "Inno Setup installer";
	website        = "http://fileformats.archiveteam.org/wiki/Inno_Setup_self-extracting_archive";
	ext            = [".exe"];
	forbidExtMatch = true;
	keepFilename   = true;
	magic          = [/^Inno Setup installer$/, "Installer: Inno Setup Module", "zlib-komprimierte Inno Setup Daten", /^Inno Setup data$/];
	auxFiles       = async (input, otherFiles) =>
	{
		const archiveFiles = [];
		for(const otherFile of otherFiles)
		{
			if(otherFile.size<5)
				continue;
			const header = await fileUtil.readFileBytes(otherFile.absolute, 5);
			if(header.getString(0, 5)==="idska")
				archiveFiles.push(otherFile);
		}
		return archiveFiles.length ? archiveFiles : false;
	};
	converters = dexState =>
	{
		const r = [];
		
		// only use innoextract if we have actual aux files, as it doesn't handle extracting as much stuff from stand-alone exe files as innounp does (1674007302_setup.exe)
		if(dexState.f.files?.aux?.length)
			r.push("innoextract");

		// skip including the aux files here, as they are often huge and if innoextract didn't handle them, likely these windows tools won't either
		r.push("innounp[noAux]", "cmdTotal[noAux][wcx:InstExpl.wcx]");
		return r;
	};
}
