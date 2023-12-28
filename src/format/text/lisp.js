import {Format} from "../../Format.js";

export class lisp extends Format
{
	name           = "Lisp/Scheme";
	website        = "http://fileformats.archiveteam.org/wiki/LISP";
	ext            = [".lsp"];
	forbidExtMatch = true;
	magic          = ["Lisp/Scheme program"];
	untouched      = true;
	metaProvider   = ["text"];
}
