import {Format} from "../../Format.js";

export class epub extends Format
{
	name           = "EPUB";
	website        = "http://fileformats.archiveteam.org/wiki/EPUB";
	ext            = [".epub"];
	forbidExtMatch = true;
	magic          = ["EPUB document", "Open Publication Structure eBook"];
	converters     = ["ebook_convert"];
}
