import {Format} from "../../Format.js";

export class playStationArtoonWMW extends Format
{
	name           = "PlayStation Artoon WMW Audio";
	ext            = [".wmw"];
	forbidExtMatch = true;
	magic          = ["PlayStation Artoon WMW (wmw)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:wmw][outType:mp3]"];
}
