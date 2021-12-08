import {xu} from "xu";
import {Format} from "../../Format.js";

export class amosPicturePacker extends Format
{
	name       = "AMOS Picture Packer";
	ext        = [".bin"];
	mimeType   = "image/x-amos-picturepacker";
	priority   = this.PRIORITY.LOW;
	idCheck    = inputFile => inputFile.size<=xu.MB*2;	// .bin is so generic, only try converting if less than 2MB, otherwise it's unlikely to be this format
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
