import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class innoSetupInstaller extends Format
{
	name           = "Inno Setup installer";
	website        = "http://fileformats.archiveteam.org/wiki/Inno_Setup_self-extracting_archive";
	ext            = [".exe"];
	forbidExtMatch = true;
	keepFilename   = true;
	magic          = [/^Inno Setup installer$/, "Installer: Inno Setup Module", "zlib-komprimierte Inno Setup Daten", /^Inno Setup data$/, "overlay: archive/innoSetupArchive", "overlay: archive/innoSetupInstaller"];
	auxFiles       = async (input, otherFiles) =>
	{
		const archiveFiles = [];
		for(const otherFile of otherFiles)
		{
			if(otherFile.size<7)
				continue;
			const headerString = (await fileUtil.readFileBytes(otherFile.absolute, 7)).getString(0, 7);
			if(["idska32", "Inno Se", "My Inno", /^i\d\.\d\.\d/, /^i\d{3}/].some(v => (typeof v==="string" ? headerString.startsWith(v) : v.test(headerString))))
				archiveFiles.push(otherFile);
		}
		return archiveFiles.length ? archiveFiles : false;
	};
	converters = ["innoextract"];
}
