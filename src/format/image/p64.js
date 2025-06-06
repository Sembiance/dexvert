import {Format} from "../../Format.js";

export class p64 extends Format
{
	name       = "Picasso 64";
	website    = "http://fileformats.archiveteam.org/wiki/Picasso_64";
	ext        = [".p64"];
	mimeType   = "image/x-picasso-64";
	magic      = ["Picasso 64 Image", "Picasso 64 :p64:"];
	weakMagic  = true;
	trustMagic = true;
	fileSize   = 10050;
	converters = ["recoil2png", "nconvert[format:p64]", `abydosconvert[format:${this.mimeType}]`, "view64"];
}
