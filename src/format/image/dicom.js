import {Format} from "../../Format.js";

export class dicom extends Format
{
	name       = "DICOM Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/DICOM";
	ext        = [".dcm", ".dic"];
	mimeType   = "application/dicom";
	magic      = ["DICOM medical imaging bitmap", "Digital Imaging and Communications in Medicine File Format", "DICOM medical imaging data", /^fmt\/574( |$)/];
	weakMagic  = ["DICOM medical imaging bitmap (w/o header)"];
	converters = [`abydosconvert[format:${this.mimeType}]`, "iconvert[strongMatch]", "gimp", "paintDotNet[strongMatch]", "canvas[strongMatch]"];
}
