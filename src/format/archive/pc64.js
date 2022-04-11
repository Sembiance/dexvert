import {Format} from "../../Format.js";

export class pc64 extends Format
{
	name           = "PC64 Container";
	ext            = [".p00", ".s00", ".r00", ".u00"];
	forbidExtMatch = true;
	magic          = ["PC64 flexible container format", "PC64 Emulator file"];
	converters     = ["DirMaster"];
}
