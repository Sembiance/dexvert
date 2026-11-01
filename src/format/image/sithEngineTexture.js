import {Format} from "../../Format.js";

export class sithEngineTexture extends Format
{
	name           = "Sith Engine Texture";
	ext            = [".mat"];
	forbidExtMatch = true;
	magic          = ["Sith Engine indexed-color texture format", /^geViewer: GOB_GOB_2_MAT_MAT( |$)/];
	auxFiles       = (input, otherFiles) =>
	{
		// no real way to tell which .cmp file goes with each .mat without going "up" to find different .gob files and checking their .jkl files, so gameextractor will do it's best guess from all the .cmp files
		const supportFiles = otherFiles.filter(o => o.ext.toLowerCase()===".cmp");
		return supportFiles.length===0 ? false : supportFiles;
	};
	keepFilename = true;
	converters   = ["gameextractor[renameOut][codes:GOB_GOB_2_MAT_MAT]"];
}
