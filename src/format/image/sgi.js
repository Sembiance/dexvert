import {Format} from "../../Format.js";

export class sgi extends Format
{
	name         = "Silicon Graphics Image";
	website      = "http://fileformats.archiveteam.org/wiki/SGI_(image_file_format)";
	ext          = [".sgi", ".bw", ".rgba", ".rgb"];
	mimeType     = "image/x-sgi";
	magic        = ["Silicon Graphics bitmap", "Silicon Graphics RGB bitmap", "SGI image data"];
	metaProvider = ["image"];
	converters   = ["convert", "nconvert", "gimp", `abydosconvert[format:${this.mimeType}]`, "hiJaakExpress"];
}
