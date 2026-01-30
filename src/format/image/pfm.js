import {Format} from "../../Format.js";

export class pfm extends Format
{
	name           = "Portable Float Map";
	website        = "http://fileformats.archiveteam.org/wiki/PFM_(Portable_Float_Map)";
	ext            = [".pfm"];
	forbidExtMatch = true;
	mimeType       = "image/x-portable-floatmap";
	magic          = ["Portable Float Map color bitmap", "piped pfm sequence (pfm_pipe)", "PFM :pfm:"];
	metaProvider   = ["image"];
	converters     = ["convert", "wuimg[format:pnm]", `abydosconvert[format:${this.mimeType}]`, "nconvert[format:pfm]", "tomsViewer[hasExtMatch]"];
}
