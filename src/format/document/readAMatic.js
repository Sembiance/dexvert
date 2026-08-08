import {Format} from "../../Format.js";

export class readAMatic extends Format
{
	name           = "Read-A-Matic";
	website        = "http://fileformats.archiveteam.org/wiki/Read-A-Matic";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Read-A-Matic", "16bit DOS Read-A-Matic Executable"];
	converters     = ["deark[module:readamatic][opt:text:encconv=0]"];
}
