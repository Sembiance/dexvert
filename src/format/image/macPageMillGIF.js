import {Format} from "../../Format.js";

export class macPageMillGIF extends Format
{
	name           = "Mac PageMill's GIF Bitmap";
	ext            = [".gif"];
	forbidExtMatch = true;
	magic          = ["Mac PageMill's GIF bitmap"];
	converters     = ["graphicWorkshopProfessional", "imageAlchemy"]
}
