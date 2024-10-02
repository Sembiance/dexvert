import {Format} from "../../Format.js";

export class pgm extends Format
{
	name         = "Portable Greyscale";
	website      = "http://fileformats.archiveteam.org/wiki/Netpbm_formats";
	ext          = [".pgm", ".pnm"];
	mimeType     = "image/x-portable-graymap";
	magic        = ["Portable GrayMap bitmap (ASCII)", "Portable GrayMap bitmap (binary)", "Portable Grey Map", "image/x-portable-graymap", "piped pgm sequence (pgm_pipe)", /^Netpbm image data.*greymap/, /^fmt\/(406|407)( |$)/];
	weakMagic    = ["Portable GrayMap bitmap (ASCII)"];
	metaProvider = ["image"];
	converters   = ["convert", "iio2png", "gimp", "wuimg", "paintDotNet", "hiJaakExpress", "canvas", "tomsViewer"];
	verify       = ({meta}) => meta.width>2 && meta.height>2;
}
