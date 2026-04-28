import {Format} from "../../Format.js";

export class delphineCIN extends Format
{
	name           = "Delphine CIN Video";
	website        = "https://wiki.multimedia.cx/index.php/Delphine_CIN";
	ext            = [".cin"];
	forbidExtMatch = true;
	magic          = ["Delphine CIN video"];
	converters     = ["vibe2avi"];
}
