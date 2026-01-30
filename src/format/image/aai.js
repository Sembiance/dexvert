import {Format} from "../../Format.js";

export class aai extends Format
{
	name         = "Dune AAI Image";
	website      = "http://fileformats.archiveteam.org/wiki/AAI";
	ext          = [".aai"];
	mimeType     = "image/x-dune";
	metaProvider = ["image"];
	converters   = ["convert", "wuimg[format:aai]"];	// "tomsViewer"
}
