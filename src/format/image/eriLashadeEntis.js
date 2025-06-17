import {Format} from "../../Format.js";

export class eriLashadeEntis extends Format
{
	name           = "ERI (Lashade Entis)";
	website        = "http://fileformats.archiveteam.org/wiki/ERI_(Lashade_Entis)";
	ext            = [".eri"];
	forbidExtMatch = true;
	magic          = ["ERI (Lashade Entis) raster graphics"];
	converters     = ["nconvertWine"];
}
