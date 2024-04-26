import {Format} from "../../Format.js";

export class hippel extends Format
{
	name         = "Hippel Module";
	website      = "http://fileformats.archiveteam.org/wiki/Hippel";
	ext          = [".hip", ".hp", ".hip7", ".hipc", ".soc", ".sog", ".hst", ".mcmd"];
	matchPreExt  = true;
	magic        = ["Hippel module", "Hippel 7V module", "Hippel COmpressed SOng module", "Hippel-COSO Module sound file"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "uade123[player:JochenHippel_UADE]"];
}
