import {Format} from "../../Format.js";

export class ppm extends Format
{
	name         = "Portable Pixmap";
	website      = "http://fileformats.archiveteam.org/wiki/Netpbm_formats";
	ext          = [".ppm", ".pnm"];
	mimeType     = "image/x-portable-pixmap";
	magic        = ["Portable PixMap bitmap", "Portable Pixel Map", "image/x-portable-pixmap", /^Netpbm image data,? .*pixmap/, /^fmt\/408( |$)/, /^x-fmt\/178( |$)/];
	idMeta       = ({macFileType}) => macFileType==="PPGM";
	metaProvider = ["image"];
	converters   = ["convert", "iio2png", "gimp", "wuimg", "paintDotNet", "hiJaakExpress", "canvas", "tomsViewer[matchType:magic]", "pv[matchType:magic]"];
}
