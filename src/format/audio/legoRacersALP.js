import {Format} from "../../Format.js";

export class legoRacersALP extends Format
{
	name           = "Lego Racers ALP Audio";
	ext            = [".tun"];
	forbidExtMatch = true;
	magic          = ["Lego Racers Tune/music data", "LEGO Racers ALP (alp)"];
	converters     = ["ffmpeg[format:alp][outType:mp3]"];
}
