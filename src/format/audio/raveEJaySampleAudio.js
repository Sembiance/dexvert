import {Format} from "../../Format.js";

export class raveEJaySampleAudio extends Format
{
	name           = "Rave eJay sample audio";
	ext            = [".pxd"];
	forbidExtMatch = true;
	magic          = ["Rave eJay sample audio"];
	converters     = ["vibe2wav[renameOut]"];
}
