import {Format} from "../../Format.js";

export class paintShopProBrowserCache extends Format
{
	name       = "PaintShop Pro Browser Cache";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop_Pro_Browser_Cache";
	ext        = [".jbf"];
	magic      = ["PaintShop Pro Browser cache", /^fmt\/217( |$)/];
	converters = ["deark"];
}
