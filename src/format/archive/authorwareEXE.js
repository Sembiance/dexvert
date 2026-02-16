import {Format} from "../../Format.js";

export class authorwareEXE extends Format
{
	name           = "Authorware Wrapped EXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["overlay: archive/authorware"];
	converters     = ["exeOverlayExtract[ext:.app] -> dexvert[asFormat:archive/authorware]"];
}
