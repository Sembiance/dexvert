import {Format} from "../../Format.js";

export class binkEXE extends Format
{
	name           = "Bink EXE Wrapper";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["overlay: video/bink"];
	converters     = ["exeOverlayExtract[ext:.bik] -> dexvert[asFormat:video/bink]"];
}
