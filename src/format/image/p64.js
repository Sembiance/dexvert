import {Format} from "../../Format.js";

export class p64 extends Format
{
	name       = "Picasso 64";
	website    = "http://fileformats.archiveteam.org/wiki/Picasso_64";
	ext        = [".p64"];
	mimeType   = "image/x-picasso-64";
	magic      = ["Picasso 64 Image"];
	weakMagic  = true;
	trustMagic = true;
	fileSize   = 10050;
	converters = ["nconvert", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64"];
}
