import {Format} from "../../Format.js";

export class paintShopPro extends Format
{
	name       = "PaintShop Pro";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop_Pro";
	ext        = [".psp", ".pspimage", ".pspbrush"];
	magic      = ["Paint Shop Pro Image", "Corel Paint Shop Pro Bild Datei", /^Paint Shop Pro :(psp|pspb|pspf|tub):$/, /^fmt\/(348|349)( |$)/, /^x-fmt\/(233|234|297|298|376|377)( |$)/];
	converters = ["nconvert[format:psp]", "nconvert[format:tub]", "gimp", "canvas"];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
