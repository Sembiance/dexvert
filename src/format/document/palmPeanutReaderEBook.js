import {Format} from "../../Format.js";

export class palmPeanutReaderEBook extends Format
{
	name           = "Palm PeanutReader e-book";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["PeanutPress PalmOS document", "Palm PeanutReader e-book"];
	converters     = ["ebook_convert"];
}
