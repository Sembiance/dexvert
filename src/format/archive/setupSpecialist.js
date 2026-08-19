import {Format} from "../../Format.js";

export class setupSpecialist extends Format
{
	name           = "Setup Specialist Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: Setup-Specialist"];
	keepFilename   = true;
	auxFiles       = (input, otherFiles) => (otherFiles.filter(file => (/\.\d$/).test(file.ext.toLowerCase())).length ?  otherFiles.filter(file => (/\.\d$/).test(file.ext.toLowerCase())) : false);
	converters     = ["vibeExtract"];
}
