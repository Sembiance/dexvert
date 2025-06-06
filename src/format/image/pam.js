import {Format} from "../../Format.js";

export class pam extends Format
{
	name         = "Portable Arbitrary Map";
	website      = "http://fileformats.archiveteam.org/wiki/Portable_Arbitrary_Map";
	ext          = [".pam"];
	mimeType     = "image/x-portable-arbitrarymap";
	magic        = ["Portable Arbitrary Map bitmap", "Portable Any Map", "Netpbm PAM image file", "piped pam sequence (pam_pipe)", "PAM :pam:", /^fmt\/405( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "iio2png", "nconvert[format:pam]", "tomsViewer", "paintDotNet"];
}
