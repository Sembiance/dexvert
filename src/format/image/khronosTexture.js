import {Format} from "../../Format.js";

export class khronosTexture extends Format
{
	name           = "Khronos Texture";
	ext            = [".ktx", ".dat", ".ktx2"];
	forbidExtMatch = true;
	mimeType       = "image/ktx";
	magic          = ["Khronos Texture", "image/ktx", /^Khronos KTX texture/, /^fmt\/970( |$)/];
	weakMagic      = true;	// only due to not being supported right now
	unsupported    = true;	// only 3 unique files on discmaster and couldn't actually convert with abydos despite it claiming support
	//converters     = [`abydosconvert[format:${this.mimeType}]`, `abydosconvert[format:image/ktx2]`];
}
