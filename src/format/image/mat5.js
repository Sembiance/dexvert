import {Format} from "../../Format.js";

export class mat5 extends Format
{
	name           = "Matlab MAT";
	website        = "http://fileformats.archiveteam.org/wiki/MAT";
	ext            = [".mat"];
	forbidExtMatch = true;
	mimeType       = "application/x-matlab-data";
	magic          = ["Matlab Level 5 MAT-File", "Matlab v5 mat-file", "Matlab MAT-File", "image/mat5", /^fmt\/806( |$)/];
	notes          = "I believe a .mat file can contain more than images, thus maybe this should be an archive, but right now we only support converting images.";
	metaProvider   = ["image"];
	converters     = ["convert[format:mat]"];
	verify         = ({meta}) => meta.colorCount>1;
}
