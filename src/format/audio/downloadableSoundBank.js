import {Format} from "../../Format.js";

export class downloadableSoundBank extends Format
{
	name           = "Downloadable Sound Bank";
	website        = "https://en.wikipedia.org/wiki/DLS_format";
	ext            = [".dls"];
	forbidExtMatch = true;
	magic          = ["DownLoadable Sound bank"];
	converters     = ["awaveStudio"];
}
