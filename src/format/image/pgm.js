import {Format} from "../../Format.js";

export class pgm extends Format
{
	name         = "Portable Greyscale";
	website      = "http://fileformats.archiveteam.org/wiki/PGM";
	ext          = [".pgm", ".pnm"];
	mimeType     = "image/x-portable-graymap";
	magic        = ["Portable GrayMap bitmap", "Portable Grey Map", /^Netpbm image data .*greymap$/, /^fmt\/(406|407)( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "gimp", "hiJaakExpress", "canvas", "tomsViewer"];
	verify       = ({meta}) => meta.width>2 && meta.height>2;
}
