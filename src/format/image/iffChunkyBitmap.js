import {Format} from "../../Format.js";

export class iffChunkyBitmap extends Format
{
	name           = "IFF Chunky bitmap";
	ext            = [".ciff"];
	forbidExtMatch = true;
	magic          = ["IFF Chunky bitmap"];
	converters     = ["wuimg[format:chky]"];
}
