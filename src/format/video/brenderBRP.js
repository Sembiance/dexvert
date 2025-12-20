import {Format} from "../../Format.js";

export class brenderBRP extends Format
{
	name           = "Blazing Rendered BRP Video";
	website        = "https://en.wikipedia.org/wiki/Argonaut_Games#BRender";
	ext            = [".brp"];
	forbidExtMatch = true;
	magic          = ["BRender BRP", "Argonaut Games BRP (argo_brp)"];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg[format:argo_brp]"];
}
