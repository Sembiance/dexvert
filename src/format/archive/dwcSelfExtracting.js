import {Format} from "../../Format.js";

export class dwcSelfExtracting extends Format
{
	name           = "DWS Self-Extracting Archive";
	website        = "http://fileformats.archiveteam.org/wiki/DWC";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["DOS DWC SFX Executable"];
	converters     = ["dosEXEExtract"];
}
