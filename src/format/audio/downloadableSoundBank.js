import {Format} from "../../Format.js";

export class downloadableSoundBank extends Format
{
	name           = "Downloadable Sound Bank";
	website        = "http://fileformats.archiveteam.org/wiki/Downloadable_Sounds_Banks";
	ext            = [".dls"];
	forbidExtMatch = true;
	magic          = ["DownLoadable Sound bank", "RIFF Datei: unbekannter Typ 'DLS '", /^Generic RIFF file DLS$/, "GigaSampler Sound bank", /^fmt\/955( |$)/];
	converters     = ["awaveStudio"];
}
