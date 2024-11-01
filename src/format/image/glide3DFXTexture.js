import {Format} from "../../Format.js";

export class glide3DFXTexture extends Format
{
	name       = "Glide 3DFX Texture";
	website    = "https://groups.google.com/g/comp.graphics.api.opengl/c/DOyoes__iVQ?pli=1";
	ext        = [".3df"];
	magic      = ["Glide 3DFX Texture", "3DFX texture format"];
	converters = ["texus"];
}
