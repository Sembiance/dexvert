import {Format} from "../../Format.js";

export class tinyStuff extends Format
{
	name       = "Tiny Stuff";
	website    = "http://fileformats.archiveteam.org/wiki/Tiny_Stuff";
	ext        = [".tn1", ".tn2", ".tn3", ".tn4", ".tny"];
	magic      = ["Tiny Stuff format bitmap", "deark: tinystuff", "Tiny :tiny:"];
	mimeType   = "image/x-tiny-stuff";
	converters = ["wuimg[format:tiny]", "recoil2png[format:TNY,TN1,TN2,TN3,TN4]", "deark[module:tinystuff]", "nconvert[format:tiny][matchType:magic][hasExtMatch]", `abydosconvert[matchType:magic][hasExtMatch][format:${this.mimeType}]`];
}
