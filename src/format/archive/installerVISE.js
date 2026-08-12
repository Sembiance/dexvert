import {Format} from "../../Format.js";

export class installerVISE extends Format
{
	name           = "Installer VISE Package";
	website        = "https://en.wikipedia.org/wiki/Installer_VISE";
	ext            = [".mac"];
	forbidExtMatch = true;
	magic          = ["Installer VISE Mac package", "Installer: Vise"];
	keepFilename   = true;
	auxFiles       = (input, otherFiles) => (otherFiles.filter(file => file.ext.toLowerCase()===".data").length ?  otherFiles.filter(file => file.ext.toLowerCase()===".data") : false);
	idMeta         = ({macFileCreator}) => macFileCreator==="VIS3";
	converters     = ["vibeExtract"];
}
