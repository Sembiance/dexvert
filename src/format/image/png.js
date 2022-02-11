import {Format} from "../../Format.js";

const _PNG_MAGIC = ["Portable Network Graphics", "PNG image data"];
export {_PNG_MAGIC};

export class png extends Format
{
	name            = "Portable Network Graphic";
	website         = "http://fileformats.archiveteam.org/wiki/PNG";
	ext             = [".png"];
	forbidExtMatch  = true;
	mimeType        = "image/png";
	magic           = _PNG_MAGIC;
	untouched       = dexState => dexState.meta.width && dexState.meta.height;
	verifyUntouched = dexState => dexState.meta.format!=="PNG";
	fallback        = true;
	metaProvider    = ["image"];
}
