import {Format} from "../../Format.js";

export class png extends Format
{
	name             = "Portable Network Graphic";
	website          = "http://fileformats.archiveteam.org/wiki/PNG";
	ext              = [".png"];
	forbidExtMatch   = true;
	mimeType         = "image/png";
	magic            = ["Portable Network Graphics", "PNG image data", "Mac PNG bitmap (MacBinary)", "PNG Plus", "PNG Bild", /^fmt\/(11|12|13|935)( |$)/];
	untouched        = dexState => dexState.meta.width && dexState.meta.height;
	verifyUntouched  = dexState =>
	{
		if(dexState.hasMagics(/^fmt\/935( |$)/))
			dexState.meta.animated = true;

		return dexState.meta.format!=="PNG";
	};
	fallback         = true;
	confidenceAdjust = () => 25; // Adjust confidence so it's above fileSize matches, since being an image many things can convert with the same tools
	metaProvider     = ["image"];
}
