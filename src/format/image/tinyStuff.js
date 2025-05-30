import {Format} from "../../Format.js";

export class tinyStuff extends Format
{
	name       = "Tiny Stuff";
	website    = "http://fileformats.archiveteam.org/wiki/Tiny_Stuff";
	ext        = [".tn1", ".tn2", ".tn3", ".tn4", ".tny"];
	magic      = ["Tiny Stuff format bitmap", "deark: tinystuff"];
	mimeType   = "image/x-tiny-stuff";
	converters = ["recoil2png", "deark[module:tinystuff]", "nconvert[matchType:magic][hasExtMatch]", `abydosconvert[matchType:magic][hasExtMatch][format:${this.mimeType}]`];
}
