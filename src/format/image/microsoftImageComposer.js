import {Format} from "../../Format.js";

export class microsoftImageComposer extends Format
{
	name           = "Microsoft Image Composer";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Image_Composer";
	ext            = [".mic"];
	forbidExtMatch = true;
	magic          = ["Microsoft Image Composer graphics"];
	converters     = ["photoDraw"];
}
