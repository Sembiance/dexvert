import {Format} from "../../Format.js";

export class vicar extends Format
{
	name         = "Video Image Communication and Retrieval";
	website      = "http://fileformats.archiveteam.org/wiki/VICAR";
	ext          = [".vicar", ".vic", ".img"];
	mimeType     = "image/x-vicar";
	magic        = ["VICAR JPL image bitmap", "PDS (VICAR) image data", /^fmt\/383( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`];
}
