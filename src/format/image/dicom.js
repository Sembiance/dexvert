import {Format} from "../../Format.js";

export class dicom extends Format
{
	name       = "DICOM Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/DICOM";
	ext        = [".dcm", ".dic"];
	mimeType   = "application/dicom";
	magic      = ["DICOM medical imaging bitmap", "Digital Imaging and Communications in Medicine File Format", "DICOM medical imaging data", "application/dicom", "DICOM :dicom:", /^fmt\/574( |$)/];
	converters = [
		"nconvert[format:dicom]", "iconvert[strongMatch]", "gimp", `abydosconvert[format:${this.mimeType}]`,
		"noesis[type:image][matchType:magic]", "paintDotNet[strongMatch][matchType:magic][hasExtMatch]", "canvas[strongMatch][matchType:magic][hasExtMatch]"
	];
}
