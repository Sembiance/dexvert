import {Format} from "../../Format.js";

export class steamInstallSystem extends Format
{
	name           = "Steam Install System";
	ext            = [".sid"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SID( |$)/];
	keepFilename   = true;
	auxFiles       = (input, otherFiles) => otherFiles.filter(file => file.ext.toLowerCase()===".sim");
	converters     = ["gameextractor[codes:SID]"];
}
