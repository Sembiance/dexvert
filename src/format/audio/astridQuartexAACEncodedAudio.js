import {Format} from "../../Format.js";

export class astridQuartexAACEncodedAudio extends Format
{
	name           = "Astrid/Quartex AAC encoded audio";
	website        = "https://web.archive.org/web/20090319015937/http://www.rjamorim.com/rrw/astrid.html";
	ext            = [".aac"];
	forbidExtMatch = true;
	magic          = ["Astrid/Quartex AAC encoded audio"];
	converters     = ["astridAACDEC"];
}
