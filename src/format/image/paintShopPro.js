import {Format} from "../../Format.js";

export class paintShopPro extends Format
{
	name       = "PaintShop";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop_Pro";
	ext        = [".psp", ".pspimage", ".pspbrush"];
	magic      = ["Paint Shop Pro Image", "Corel Paint Shop Pro Bild Datei", /^x-fmt\/(233|234|297|376|377)( |$)/];
	converters = ["nconvert", "gimp", "canvas"];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
