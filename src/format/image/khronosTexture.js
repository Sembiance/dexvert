import {Format} from "../../Format.js";

export class khronosTexture extends Format
{
	name           = "Khronos Texture";
	ext            = [".ktx", ".dat", ".ktx2"];
	forbidExtMatch = true;
	mimeType       = "image/ktx";
	magic          = ["Khronos Texture", "image/ktx", /^Khronos KTX texture/, /^fmt\/970( |$)/];
	weakMagic      = true;	// only due to being unsupported right now
	unsupported    = true;
	//converters     = [`abydosconvert[format:${this.mimeType}]`, `abydosconvert[format:image/ktx2]`];	// abydos claims support, but could not get it to convert
}
