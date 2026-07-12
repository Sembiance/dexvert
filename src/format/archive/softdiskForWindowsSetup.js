import {Format} from "../../Format.js";

export class softdiskForWindowsSetup extends Format
{
	name           = "Softdisk for Windows Setup";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Softdisk for Windows Setup"];
	metaProvider   = ["winedump", "exiftool"];
	auxFiles       = (input, otherFiles) => (otherFiles?.some(file => file.ext.toLowerCase()===".w02") ? otherFiles.filter(file => file.ext.toLowerCase()===".w02") : false);
	keepFilename   = true;
	converters     = ["vibeExtract"];
}
