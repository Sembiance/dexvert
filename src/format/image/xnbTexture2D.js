import {Format} from "../../Format.js";

export class xnbTexture2D extends Format
{
	name       = "XNA/XNB Texture2D";
	ext        = [".texture2d"];
	idCheck    = inputFile => (inputFile.size%4)===0;
	converters = ["vibe2png"];
}
