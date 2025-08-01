import {Format} from "../../Format.js";

export class winMiPS extends Format
{
	name           = "WinMiPS";
	website        = "http://fileformats.archiveteam.org/wiki/WinMiPS";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = ["WinMIPS :winm:"];
	converters     = ["nconvert[format:winm]"];
}
