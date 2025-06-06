import {Format} from "../../Format.js";

export class viff extends Format
{
	name         = "Khoros Visualization Image";
	website      = "http://fileformats.archiveteam.org/wiki/VIFF";
	ext          = [".viff", ".xv"];
	mimeType     = "image/x-viff";
	magic        = ["Khoros Visualization Image File Format", "Khoros Visualization image file :viff:"];
	metaProvider = ["image"];
	converters   = ["convert[format:VIFF]", "nconvert[format:viff]", `abydosconvert[format:${this.mimeType}]`, "imconv[format:viff]", "tomsViewer[matchType:magic][hasExtMatch]"];
	verify       = ({meta}) => meta.height>2 && meta.width>2 && meta.width<3000 && meta.height<3000;
}
