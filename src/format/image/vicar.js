import {Format} from "../../Format.js";

export class vicar extends Format
{
	name           = "Video Image Communication and Retrieval";
	website        = "http://fileformats.archiveteam.org/wiki/VICAR";
	ext            = [".vicar", ".vic", ".img"];
	forbidExtMatch = [".img"];
	mimeType       = "image/x-vicar";
	magic          = ["VICAR JPL image bitmap", "PDS (VICAR) image data", /^VICAR image data/, "Video Image Communication And Retrieval :vicar:", /^fmt\/383( |$)/];
	idMeta          = ({macFileType, macFileCreator}) => ["VICR", "VLUT"].includes(macFileType) && macFileCreator==="PXPS";
	metaProvider   = ["image"];
	converters     = ["convert", "nconvert[format:vicar]", `abydosconvert[format:${this.mimeType}]`];
	verify         = ({meta}) => meta.width>=1 && meta.height>=1;
}
