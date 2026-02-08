import {Format} from "../../Format.js";

export class innoSetupInstaller extends Format
{
	name           = "Inno Setup installer";
	website        = "http://fileformats.archiveteam.org/wiki/Inno_Setup_self-extracting_archive";
	ext            = [".exe"];
	forbidExtMatch = true;
	keepFilename   = true;
	magic          = ["Inno Setup installer", "Installer: Inno Setup Module", "zlib-komprimierte Inno Setup Daten", /^Inno Setup data$/];
	auxFiles       = (input, otherFiles) =>
	{
		const binFiles = otherFiles.filter(file => file.ext.toLowerCase()===".bin");
		return binFiles.length ? binFiles : false;
	};
	converters = [
		"innoextract",

		// skip including the .bin files here, as they are often huge and if innoextract didn't handle them, likely these windows tools won't either
		"innounp[noAux]", "cmdTotal[noAux][wcx:InstExpl.wcx]"
	];
}
