import {Format} from "../../Format.js";

export class riffPalette extends Format
{
	name           = "RIFF Palette";
	ext            = [".pal"];
	forbidExtMatch = true;
	magic          = ["RIFF Palette", /^RIFF \((little|big)-endian\) data, palette/, /^geViewer: PAL_RIFF( |$)/, /^geViewer: PAL_RIFF( |$)/, /^fmt\/624( |$)/];
	converters     = ["gameextractor[codes:PAL_RIFF][renameOut]"];
}

