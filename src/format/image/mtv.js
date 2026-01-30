import {Format} from "../../Format.js";

export class mtv extends Format
{
	name           = "MTV Ray-Tracer";
	website        = "http://fileformats.archiveteam.org/wiki/MTV_ray_tracer_bitmap";
	ext            = [".mtv", ".pic"];
	forbidExtMatch = [".pic"];
	mimeType       = "image/x-mtv";
	magic          = ["zlib compressed data", "MTV / Rayshade :mtv:"];
	weakMagic      = true;
	metaProvider   = ["image"];
	converters     = ["convert", "nconvert[format:mtv]", "wuimg[format:pnm]", `abydosconvert[format:${this.mimeType}]`, "tomsViewer"];
}
