import {xu} from "xu";
import {Format} from "../../Format.js";

export class amosPicturePacker extends Format
{
	name       = "AMOS Picture Packer";
	ext        = [".bin"];
	mimeType   = "image/x-amos-picturepacker";
	priority   = this.PRIORITY.LOW;
	idCheck    = inputFile => inputFile.size<=xu.KB*50;	// .bin is so generic, only try converting if less than 50KB as I've never seen an image in this format be larger than this
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
