import {Format} from "../../Format.js";

export class photoCDAudio extends Format
{
	name           = "PhotoCD Audio";
	ext            = [".pcd"];
	forbidExtMatch = true;
	filename       = [/^audio\d+\.pcd$/i];
	converters     = ["sox[type:cdda]"];
	notes          = "Files audio03.pcd and audio04.pcd don't convert properly. If I use sox type 'lpc' I can kinda hear some structure, so not sure what variant these files are.";
}
