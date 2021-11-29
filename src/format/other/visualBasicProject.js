import {Format} from "../../Format.js";

export class visualBasicProject extends Format
{
	name           = "Visual Basic Project";
	website        = "http://fileformats.archiveteam.org/wiki/Visual_Basic_project_file";
	ext            = [".mak"];
	forbidExtMatch = true;
	magic          = ["Visual Basic project"];
	converters     = ["strings"];
}
