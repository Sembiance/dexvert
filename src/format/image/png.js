import {Format} from "../../Format.js";

export class png extends Format
{
	name             = "Portable Network Graphic";
	website          = "http://fileformats.archiveteam.org/wiki/PNG";
	ext              = [".png"];
	forbidExtMatch   = true;
	mimeType         = "image/png";
	magic            = [
		// generic
		"Portable Network Graphics", "PNG image data", "Mac PNG bitmap (MacBinary)", "PNG Plus", "PNG Bild", "PNG image, ", "image/png", "image/apng", "piped png sequence (png_pipe)", "Animated Portable Network Graphics (apng)",
		/^fmt\/(11|12|13|935)( |$)/,

		// specific
		"Fireworks PNG bitmap", "Krita Paint Op Preset"
	];
	idMeta           = ({macFileType}) => macFileType==="PNGf";
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
