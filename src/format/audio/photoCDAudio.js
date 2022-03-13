import {Format} from "../../Format.js";

export class photoCDAudio extends Format
{
	name           = "PhotoCD Audio";
	ext            = [".pcd"];
	forbidExtMatch = true;
	filename       = [/^audio\d+\.pcd$/i];
	converters     = ["sox[type:cdda]"];
}
